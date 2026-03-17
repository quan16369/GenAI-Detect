import argparse
import os

import joblib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

from utils import read_jsonl, write_jsonl, normalize_text, abstain_score, clamp_score


def _resolve_model_path(model_path: str) -> str:
    if os.path.exists(model_path):
        return model_path
    raise FileNotFoundError(
        f"Model file not found: {model_path}. "
        "Pass an explicit valid path."
    )


def load_tfidf(model_path: str):
    resolved = _resolve_model_path(model_path)
    obj = joblib.load(resolved)
    return obj["pipeline"], obj["normalized"]


def tfidf_predict_one(pipeline, normalized: bool, text: str) -> float:
    if normalized:
        text = normalize_text(text)
    prob = pipeline.predict_proba([text])[0, 1]
    return float(prob)


class DebertaPredictor:
    def __init__(self, model_dir: str, device: str = None):
        if not os.path.isdir(model_dir):
            raise FileNotFoundError(
                f"Model directory not found: {model_dir}. "
                "Pass an explicit valid directory."
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        self.normalized = False
        meta_path = os.path.join(model_dir, "meta.txt")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line == "normalized=True":
                        self.normalized = True

    @torch.no_grad()
    def predict_one(self, text: str) -> float:
        if self.normalized:
            text = normalize_text(text)

        enc = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}
        logits = self.model(**enc).logits
        prob = torch.softmax(logits, dim=-1)[0, 1].item()
        return float(prob)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("output_dir", type=str)
    parser.add_argument("--tfidf_model", type=str, default="models/tfidf.joblib")
    parser.add_argument("--deberta_raw_dir", type=str, default="models/deberta_raw")
    parser.add_argument("--deberta_norm_dir", type=str, default="models/deberta_norm")
    parser.add_argument("--w_tfidf", type=float, default=0.35)
    parser.add_argument("--w_raw", type=float, default=0.35)
    parser.add_argument("--w_norm", type=float, default=0.30)
    parser.add_argument("--abstain_band", type=float, default=0.03)
    args = parser.parse_args()

    rows = read_jsonl(args.input_file)

    tfidf_pipe, tfidf_norm = load_tfidf(args.tfidf_model)
    deberta_raw = DebertaPredictor(args.deberta_raw_dir)
    deberta_norm = DebertaPredictor(args.deberta_norm_dir)

    out_rows = []
    for row in tqdm(rows):
        text = row["text"]

        s_tfidf = tfidf_predict_one(tfidf_pipe, tfidf_norm, text)
        s_raw = deberta_raw.predict_one(text)
        s_norm = deberta_norm.predict_one(text)

        score = (
            args.w_tfidf * s_tfidf
            + args.w_raw * s_raw
            + args.w_norm * s_norm
        )
        score = clamp_score(score)
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
