"""
train_worker.py — AI Operations (AIOps), Module 3 Lecture 2a
Entry point for each pod of the Kubernetes Indexed Job.
"""
import itertools, json, os, socket, time
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

N_ESTIMATORS_GRID = [50, 100, 150, 200]
MAX_DEPTH_GRID = [4, 8, 12]
GRID = list(itertools.product(N_ESTIMATORS_GRID, MAX_DEPTH_GRID))


def main():
    completion_index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    n_estimators, max_depth = GRID[completion_index % len(GRID)]

    data_path = os.environ.get("DATA_PATH", "/app/data/ml_job_dataset.csv")
    pod_name = os.environ.get("POD_NAME", socket.gethostname())
    node_name = os.environ.get("NODE_NAME", "unknown")

    print(f"[worker {completion_index}] pod={pod_name} node={node_name} "
          f"n_estimators={n_estimators} max_depth={max_depth}", flush=True)

    df = pd.read_csv(data_path)
    X = df.drop(columns=["label"])
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    t0 = time.time()
    # n_jobs=1 is DELIBERATE: each pod should use ~1 CPU core, so the parallelism story is
    # about KUBERNETES scheduling many pods, not a single RandomForest fanning out internally.
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=1)
    model.fit(X_train, y_train)
    train_seconds = time.time() - t0

    preds = model.predict(X_test)
    result = {
        "completion_index": completion_index, "n_estimators": n_estimators, "max_depth": max_depth,
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "f1_score": round(f1_score(y_test, preds), 4),
        "train_seconds": round(train_seconds, 3),
        "pod_name": pod_name, "node_name": node_name,
    }
    print("RESULT_JSON:" + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
