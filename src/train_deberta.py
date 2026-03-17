import argparse
import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score

from utils import read_jsonl, normalize_text, set_seed


@dataclass
class Example:
    text: str
    label: int


class TextDataset(Dataset):
    def __init__(self, rows: List[Dict], tokenizer, max_length: int, normalized: bool):
        self.examples = []
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.normalized = normalized

        for r in rows:
            if "label" not in r:
                continue

            text = r.get("text", "")
            if text is None:
                text = ""
            text = str(text).strip()

            if self.normalized:
                text = normalize_text(text)

            try:
                label = int(r["label"])
            except (TypeError, ValueError):
                continue
            if label not in (0, 1):
                continue
            self.examples.append(Example(text=text, label=label))

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        enc = self.tokenizer(
            ex.text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item["labels"] = torch.tensor(ex.label, dtype=torch.long)
        return item


def evaluate(model, loader, device):
    model.eval()
    probs = []
    labels = []

    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            model_inputs = {
                "input_ids": batch["input_ids"],
                "attention_mask": batch["attention_mask"],
                "labels": batch["labels"],
            }
            if "token_type_ids" in batch:
                model_inputs["token_type_ids"] = batch["token_type_ids"]

            outputs = model(**model_inputs)
            logits = outputs.logits
            p = torch.softmax(logits, dim=-1)[:, 1].detach().cpu().numpy()
            y = batch["labels"].detach().cpu().numpy()
            probs.extend(p.tolist())
            labels.extend(y.tolist())

    preds = (np.array(probs) >= 0.5).astype(int)
    f1 = f1_score(labels, preds)
    try:
        auc = roc_auc_score(labels, probs)
    except Exception:
        auc = float("nan")
    return f1, auc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", type=str, required=True)
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="microsoft/deberta-v3-base")
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-6)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--normalized", action="store_true")
    args = parser.parse_args()

    set_seed(42)
    rows = read_jsonl(args.train_file)
    labeled_rows = []
    for r in rows:
        if "label" not in r:
            continue
        try:
            label = int(r["label"])
        except (TypeError, ValueError):
            continue
        if label in (0, 1):
            labeled_rows.append(r)

    train_rows, val_rows = train_test_split(
        labeled_rows,
        test_size=0.15,
        random_state=42,
        stratify=[int(r["label"]) for r in labeled_rows],
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=2,
    )

    train_ds = TextDataset(train_rows, tokenizer, args.max_length, args.normalized)
    val_ds = TextDataset(val_rows, tokenizer, args.max_length, args.normalized)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_steps // 10),
        num_training_steps=total_steps,
    )

    best_f1 = -1.0
    os.makedirs(args.model_dir, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        pbar = tqdm(train_loader, desc=f"epoch {epoch + 1}")
        for step, batch in enumerate(pbar):
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch["labels"]
            if torch.any((labels < 0) | (labels > 1)):
                raise RuntimeError(f"Invalid labels in batch at step {step}: {labels.tolist()}")

            model_inputs = {
                "input_ids": batch["input_ids"],
                "attention_mask": batch["attention_mask"],
                "labels": batch["labels"],
            }
            if "token_type_ids" in batch:
                model_inputs["token_type_ids"] = batch["token_type_ids"]

            outputs = model(**model_inputs)
            loss = outputs.loss
            logits = outputs.logits

            if not torch.isfinite(loss) or not torch.isfinite(logits).all():
                attn = batch["attention_mask"]
                msg = (
                    f"Non-finite detected at step {step}. "
                    f"loss={loss.item() if torch.isfinite(loss) else 'nan/inf'}, "
                    f"input_ids_range=({int(batch['input_ids'].min())}, {int(batch['input_ids'].max())}), "
                    f"attn_sum_minmax=({int(attn.sum(dim=1).min())}, {int(attn.sum(dim=1).max())}), "
                    f"labels={labels.tolist()}"
                )
                raise RuntimeError(msg)

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            grad_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0,
                error_if_nonfinite=False,
            )
            if not torch.isfinite(grad_norm):
                raise RuntimeError(f"Non-finite gradient norm at step {step}: {float(grad_norm)}")
            optimizer.step()
            scheduler.step()

            pbar.set_postfix(loss=float(loss.item()))

        f1, auc = evaluate(model, val_loader, device)
        print(f"epoch={epoch+1} val_f1={f1:.6f} val_auc={auc:.6f}")

        if f1 > best_f1:
            best_f1 = f1
            model.save_pretrained(args.model_dir)
            tokenizer.save_pretrained(args.model_dir)
            with open(os.path.join(args.model_dir, "meta.txt"), "w", encoding="utf-8") as f:
                f.write(f"normalized={args.normalized}\n")
                f.write(f"max_length={args.max_length}\n")

    print(f"Saved best model to {args.model_dir}")


if __name__ == "__main__":
    main()
