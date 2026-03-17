import argparse
import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import (
    AutoConfig,
    AutoModel,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

from utils import normalize_text, read_jsonl, set_seed


@dataclass
class Example:
    text: str
    label: float


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

            label = float(r["label"])
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
        item["labels"] = torch.tensor(ex.label, dtype=torch.float32)
        return item


class MeanPoolingBinaryClassifier(nn.Module):
    def __init__(self, model_name: str):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name)
        self.backbone = AutoModel.from_pretrained(model_name, config=self.config)
        self.classifier = nn.Linear(self.config.hidden_size, 1)

    def forward_features(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state  # [B, T, H]

        input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
        sum_mask = input_mask_expanded.sum(dim=1).clamp(min=1e-9)
        embeddings = sum_embeddings / sum_mask
        return embeddings

    def forward(self, input_ids, attention_mask):
        embeddings = self.forward_features(input_ids, attention_mask)
        logits = self.classifier(embeddings).squeeze(-1)  # [B]
        return logits


def evaluate(model, loader, device):
    model.eval()
    probs = []
    labels = []

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            y = batch["labels"].to(device)

            logits = model(input_ids=input_ids, attention_mask=attention_mask)
            p = torch.sigmoid(logits)

            probs.extend(p.detach().cpu().numpy().tolist())
            labels.extend(y.detach().cpu().numpy().tolist())

    probs = np.array(probs)
    labels = np.array(labels)
    preds = (probs >= 0.5).astype(int)

    f1 = f1_score(labels.astype(int), preds)
    try:
        auc = roc_auc_score(labels, probs)
    except Exception:
        auc = float("nan")
    return f1, auc


def save_checkpoint(model, tokenizer, model_dir, normalized, max_length):
    os.makedirs(model_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_dir, "model.pt"))
    tokenizer.save_pretrained(model_dir)
    model.config.save_pretrained(model_dir)

    with open(os.path.join(model_dir, "meta.txt"), "w", encoding="utf-8") as f:
        f.write(f"normalized={normalized}\n")
        f.write(f"max_length={max_length}\n")


def build_optimizer_and_scheduler(model, train_loader, num_epochs, stage, weight_decay=0.01):
    """
    stage=1: freeze backbone, train classifier only
    stage=2: unfreeze backbone, smaller lr for backbone
    """
    if stage == 1:
        for p in model.backbone.parameters():
            p.requires_grad = False
        for p in model.classifier.parameters():
            p.requires_grad = True

        optimizer = torch.optim.AdamW(
            model.classifier.parameters(),
            lr=5e-4,
            weight_decay=weight_decay,
        )

    elif stage == 2:
        for p in model.backbone.parameters():
            p.requires_grad = True
        for p in model.classifier.parameters():
            p.requires_grad = True

        optimizer = torch.optim.AdamW(
            [
                {"params": model.backbone.parameters(), "lr": 5e-6},
                {"params": model.classifier.parameters(), "lr": 1e-4},
            ],
            weight_decay=weight_decay,
        )
    else:
        raise ValueError(f"Unknown stage: {stage}")

    total_steps = len(train_loader) * max(1, num_epochs)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_steps // 10),
        num_training_steps=max(1, total_steps),
    )
    return optimizer, scheduler


def train_one_epoch(model, loader, optimizer, scheduler, criterion, device, epoch_idx):
    model.train()
    pbar = tqdm(loader, desc=f"epoch {epoch_idx}")
    running_loss = []

    for step, batch in enumerate(pbar):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad(set_to_none=True)

        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = criterion(logits, labels)

        if torch.isnan(loss) or torch.isinf(loss):
            print(f"Skipping bad batch at step {step}: loss={loss}")
            continue

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()
        scheduler.step()

        running_loss.append(float(loss.item()))
        avg_loss = sum(running_loss[-50:]) / min(len(running_loss), 50)
        pbar.set_postfix(loss=float(loss.item()), avg=avg_loss)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", type=str, required=True)
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="microsoft/deberta-v3-base")
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--epochs_stage1", type=int, default=1)
    parser.add_argument("--epochs_stage2", type=int, default=1)
    parser.add_argument("--normalized", action="store_true")
    args = parser.parse_args()

    set_seed(42)

    rows = read_jsonl(args.train_file)
    labeled_rows = [r for r in rows if "label" in r]

    train_rows, val_rows = train_test_split(
        labeled_rows,
        test_size=0.15,
        random_state=42,
        stratify=[int(r["label"]) for r in labeled_rows],
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = MeanPoolingBinaryClassifier(args.model_name)

    train_ds = TextDataset(train_rows, tokenizer, args.max_length, args.normalized)
    val_ds = TextDataset(val_rows, tokenizer, args.max_length, args.normalized)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = nn.BCEWithLogitsLoss()
    best_f1 = -1.0

    # --------------------
    # Stage 1: classifier only
    # --------------------
    if args.epochs_stage1 > 0:
        print("Stage 1: freeze backbone, train classifier only")
        optimizer, scheduler = build_optimizer_and_scheduler(
            model=model,
            train_loader=train_loader,
            num_epochs=args.epochs_stage1,
            stage=1,
        )

        for epoch in range(args.epochs_stage1):
            train_one_epoch(
                model=model,
                loader=train_loader,
                optimizer=optimizer,
                scheduler=scheduler,
                criterion=criterion,
                device=device,
                epoch_idx=f"stage1-{epoch + 1}",
            )

            f1, auc = evaluate(model, val_loader, device)
            print(f"[stage1 epoch={epoch+1}] val_f1={f1:.6f} val_auc={auc:.6f}")

            if f1 > best_f1:
                best_f1 = f1
                save_checkpoint(
                    model=model,
                    tokenizer=tokenizer,
                    model_dir=args.model_dir,
                    normalized=args.normalized,
                    max_length=args.max_length,
                )

    # --------------------
    # Stage 2: unfreeze full model
    # --------------------
    if args.epochs_stage2 > 0:
        print("Stage 2: unfreeze backbone, fine-tune full model")
        optimizer, scheduler = build_optimizer_and_scheduler(
            model=model,
            train_loader=train_loader,
            num_epochs=args.epochs_stage2,
            stage=2,
        )

        for epoch in range(args.epochs_stage2):
            train_one_epoch(
                model=model,
                loader=train_loader,
                optimizer=optimizer,
                scheduler=scheduler,
                criterion=criterion,
                device=device,
                epoch_idx=f"stage2-{epoch + 1}",
            )

            f1, auc = evaluate(model, val_loader, device)
            print(f"[stage2 epoch={epoch+1}] val_f1={f1:.6f} val_auc={auc:.6f}")

            if f1 > best_f1:
                best_f1 = f1
                save_checkpoint(
                    model=model,
                    tokenizer=tokenizer,
                    model_dir=args.model_dir,
                    normalized=args.normalized,
                    max_length=args.max_length,
                )

    print(f"Best val_f1={best_f1:.6f}")
    print(f"Saved best model to {args.model_dir}")


if __name__ == "__main__":
    main()