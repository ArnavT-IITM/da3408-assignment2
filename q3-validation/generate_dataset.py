"""
generate_dataset.py — AI Operations (AIOps), Module 3 Lecture 2a
Generates a small, deterministic synthetic classification dataset.
"""
import argparse
import pandas as pd
from sklearn.datasets import make_classification


def generate(n_samples=6000, n_features=20, n_informative=12, n_classes=2, random_state=42):
    X, y = make_classification(
        n_samples=n_samples, n_features=n_features, n_informative=n_informative,
        n_redundant=4, n_classes=n_classes, class_sep=1.1, random_state=random_state,
    )
    columns = [f"feature_{i:02d}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=columns)
    df["label"] = y
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="ml_job_dataset.csv")
    parser.add_argument("--n-samples", type=int, default=6000)
    parser.add_argument("--n-features", type=int, default=20)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    df = generate(n_samples=args.n_samples, n_features=args.n_features, random_state=args.random_state)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df):,} rows x {df.shape[1]} columns to {args.out}")


if __name__ == "__main__":
    main()
