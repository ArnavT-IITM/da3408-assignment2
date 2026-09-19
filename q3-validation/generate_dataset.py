import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

FIRST = ["arnav", "priya", "rahul", "sneha", "vikram", "ananya", "karan", "meera"]
LAST = ["sharma", "patel", "iyer", "reddy", "gupta", "nair", "singh", "das"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "iitm.ac.in"]
N_SHARDS = 8
ROWS_PER_SHARD = 100

os.makedirs("data", exist_ok=True)

for shard in range(N_SHARDS):
    rows = []
    for i in range(ROWS_PER_SHARD):
        first, last = random.choice(FIRST), random.choice(LAST)
        rows.append({
            "user_id": shard * ROWS_PER_SHARD + i,
            "name": f"{first.title()} {last.title()}",
            "email": f"{first}.{last}{random.randint(1, 99)}@{random.choice(DOMAINS)}",
            "signup_date": str(date(2026, 1, 1) + timedelta(days=random.randint(0, 250))),
        })

    n_invalid = random.randint(3, 12)
    for i in random.sample(range(ROWS_PER_SHARD), n_invalid):
        defect = random.choice(["bad_email", "missing_name", "missing_date"])
        if defect == "bad_email":
            rows[i]["email"] = rows[i]["email"].replace("@", ".")
        elif defect == "missing_name":
            rows[i]["name"] = ""
        else:
            rows[i]["signup_date"] = ""

    pd.DataFrame(rows).to_csv(f"data/shard_{shard}.csv", index=False)
    print(f"shard_{shard}.csv: {ROWS_PER_SHARD} rows, {n_invalid} invalid")
