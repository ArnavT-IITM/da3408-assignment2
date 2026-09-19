import json
import os
import socket
import time

import pandas as pd

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
REQUIRED = ["user_id", "name", "email", "signup_date"]

index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
data_dir = os.environ.get("DATA_DIR", "/app/data")
pod_name = os.environ.get("POD_NAME", socket.gethostname())
node_name = os.environ.get("NODE_NAME", "unknown")
hold_seconds = int(os.environ.get("HOLD_SECONDS", "20"))

shard = f"shard_{index}.csv"
print(f"[worker {index}] pod={pod_name} node={node_name} shard={shard}", flush=True)

df = pd.read_csv(f"{data_dir}/{shard}")
missing_field = df[REQUIRED].isna().any(axis=1)
bad_email = ~df["email"].astype(str).str.match(EMAIL_PATTERN)
invalid = missing_field | bad_email

time.sleep(hold_seconds)

result = {
    "completion_index": index,
    "shard": shard,
    "rows": len(df),
    "invalid_rows": int(invalid.sum()),
    "missing_field": int(missing_field.sum()),
    "bad_email": int(bad_email.sum()),
    "pod_name": pod_name,
    "node_name": node_name,
}
print("RESULT_JSON:" + json.dumps(result), flush=True)
