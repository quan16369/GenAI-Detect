import argparse
import os

import joblib
import torch
import torch.nn as nn
from tqdm import tqdm
from transformers import AutoConfig, AutoModel, AutoTokenizer

from utils import abstain_score, clamp_score, normalize_text, read_jsonl, write_jsonl


def load_tfidf(model_path: str):
    obj = joblib.load(model_path)
    return obj["pipeline"], obj["normalized"]


def tfidf_predict_one(pipeline, normalized: bool, text: str) -> float:
    if normalized:
        text = normalize_text(text)
    prob = pipeline.predict_proba([text])[0, 1]
    return float(prob)


class MeanPoolingBinaryClassifier(nn.Module):
    def __init__(self, model_dir: str):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_dir)
        self.backbone = AutoModel.from_pretrained(model_dir, config=self.config)
        self.classifier = nn.Linear(self.config.hidden_size, 1)

    def forward_features(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state

        input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
        sum_mask = input_mask_expanded.sum(dim=1).clamp(min=1e-9)
        embeddings = sum_embeddings / sum_mask
        return embeddings

    def forward(self, input_ids, attention_mask):
        embeddings = self.forward_features(input_ids, attention_mask)
        logits = self.classifier(embeddings).squeeze(-1)
        return logits


class DebertaPredictor:
    def __init__(self, model_dir: str, device: str = None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = MeanPoolingBinaryClassifier(model_dir)

        state_dict_path = os.path.join(model_dir, "model.pt")
        self.model.load_state_dict(torch.load(state_dict_path, map_location="cpu"))

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        self.normalized = False
        self.max_length = 256

        meta_path = os.path.join(model_dir, "meta.txt")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line == "normalized=True":
                        self.normalized = True
                    elif line.startswith("max_length="):
                        self.max_length = int(line.split("=", 1)[1])

    @torch.no_grad()
    def predict_one(self, text: str) -> float:
        if self.normalized:
            text = normalize_text(text)

        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}

        logits = self.model(
            input_ids=enc["input_ids"],
            attention_mask=enc["attention_mask"],
        )
        prob = torch.sigmoid(logits)[0].item()
        return float(prob)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("output_dir", type=str)
    parser.add_argument("--tfidf_model", type=str, default="models/tfidf/tfidf.joblib")
    parser.add_argument("--deberta_raw_dir", type=str, default="models/deberta_raw")
    parser.add_argument("--deberta_norm_dir", type=str, default="models/deberta_norm")
    parser.add_argument("--w_tfidf", type=float, default=0.35)
    parser.add_argument("--w_raw", type=float, default=0.35)
    parser.add_argument("--w_norm", type=float, default=0.30)
    parser.add_argument("--abstain_band", type=float, default=0.03)
    parser.add_argument("--disagreement_threshold", type=float, default=0.35)
    args = parser.parse_args()

    rows = read_jsonl(args.input_file)

    tfidf_pipe, tfidf_norm = load_tfidf(args.tfidf_model)
    deberta_raw = DebertaPredictor(args.deberta_raw_dir)
    deberta_norm = DebertaPredictor(args.deberta_norm_dir)

    out_rows = []
    for row in tqdm(rows):
        text = str(row.get("text", ""))

        s_tfidf = tfidf_predict_one(tfidf_pipe, tfidf_norm, text)
        s_raw = deberta_raw.predict_one(text)
        s_norm = deberta_norm.predict_one(text)

        score = (
            args.w_tfidf * s_tfidf +
            args.w_raw * s_raw +
            args.w_norm * s_norm
        )
        score = clamp_score(score)

        spread = max(s_tfidf, s_raw, s_norm) - min(s_tfidf, s_raw, s_norm)
        if spread > args.disagreement_threshold and abs(score - 0.5) < 0.08:
            score = 0.5
        else:
            score = abstain_score(score, band=args.abstain_band)

        out_rows.append({
            "id": row["id"],
            "label": float(score),
        })

    os.makedirs(args.output_dir, exist_ok=True)
    out_file = os.path.join(args.output_dir, "predictions.jsonl")
    write_jsonl(out_file, out_rows)
    print(f"Wrote predictions to {out_file}")


if __name__ == "__main__":
    main()