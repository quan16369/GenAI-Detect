import argparse
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from utils import read_jsonl, normalize_text, set_seed


def build_texts_and_labels(rows, use_normalized: bool):
    texts = []
    labels = []
    for r in rows:
        if "label" not in r:
            continue
        text = r["text"]
        if use_normalized:
            text = normalize_text(text)
        texts.append(text)
        labels.append(int(r["label"]))
    return texts, labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", type=str, required=True)
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--normalized", action="store_true")
    args = parser.parse_args()

    set_seed(42)
    rows = read_jsonl(args.train_file)
    texts, labels = build_texts_and_labels(rows, args.normalized)

    x_train, x_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.15, random_state=42, stratify=labels
    )

    word_tfidf = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 3),
        min_df=2,
        max_features=200000,
        sublinear_tf=True,
    )

    char_tfidf = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        max_features=300000,
        sublinear_tf=True,
    )

    features = FeatureUnion([
        ("word", word_tfidf),
        ("char", char_tfidf),
    ])

    clf = LogisticRegression(
        max_iter=2000,
        C=3.0,
        solver="liblinear",
        class_weight="balanced",
    )

    pipe = Pipeline([
        ("features", features),
        ("clf", clf),
    ])

    pipe.fit(x_train, y_train)

    val_probs = pipe.predict_proba(x_val)[:, 1]
    val_pred = (val_probs >= 0.5).astype(int)

    print("TFIDF F1:", f1_score(y_val, val_pred))
    try:
        print("TFIDF ROC-AUC:", roc_auc_score(y_val, val_probs))
    except Exception:
        pass

    os.makedirs(args.model_dir, exist_ok=True)
    out_path = os.path.join(args.model_dir, "tfidf.joblib")
    joblib.dump(
        {
            "pipeline": pipe,
            "normalized": args.normalized,
        },
        out_path,
    )
    print(f"Saved TFIDF model to {out_path}")


if __name__ == "__main__":
    main()