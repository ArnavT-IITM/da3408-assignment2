# DA3408 Assignment 2

## Repository contents

| Question | Files | Evidence |
|---|---|---|
| Setup | `app/generate_dataset.py`, `app/train.py`, `app/predictor_app.py`, `data/` | - |
| Q1: naive vs. multi-stage Docker | `Dockerfile.naive`, `Dockerfile` | `evidence/q1-*.png` |
| Q2: Compose + Redis cache | `docker-compose.yml`, `app/predictor_app.py`, `scripts/cache_benchmark.sh` | `evidence/q2-*.png` |
| Q3: Kubernetes Indexed Job | `q3-validation/` | `evidence/q3-*.png` |
| Q4: Deployment, self-healing, rolling update | `k8s/deployment.yaml`, `k8s/service.yaml` | `evidence/q4-*.png` |

- `writeup.pdf`: two-page write-up covering Questions 1 to 4.
- `app/predictor_app.py`: exposes `POST /predict` (`{"text": "..."}`, returns `{"label": "spam"}` or `{"label": "ham"}`) and `GET /healthz` (200 once the model is loaded, 503 before that).
- `q3-validation/`: shard generator, validation worker, worker image, Indexed Job manifest and the results collector.
- Git tags `q1` and `q2` mark the commits at which the Q1 and Q2 evidence was captured.

The lecture's `predictor_app.py` and its Indexed Job files are committed unmodified before they were adapted. Running `git log --oneline` shows the lecture-copy commits, and `git diff` against the following commits shows what was changed.

## Setup

You need Docker (with Compose), minikube and kubectl. Create a Conda environment and install the Python packages:

```bash
conda create -n da3408-assignment2 python=3.12 -y
conda activate da3408-assignment2
pip install -r app/requirements.txt pandas kubernetes
```

Generate the dataset and train the model from the repository root. Both files are already committed, so this step is optional:

```bash
python app/generate_dataset.py
python app/train.py
```

## Question 1

```bash
docker build -f Dockerfile.naive -t spam-api:naive .
docker build -f Dockerfile -t spam-api:multistage .
docker images spam-api

docker run -d --rm --name q1 -p 8080:8080 spam-api:multistage
curl localhost:8080/healthz
curl -X POST localhost:8080/predict -H 'Content-Type: application/json' -d '{"text":"WIN a FREE iPhone now!"}'
docker stop q1
```

Both images use `python:3.12-slim`. The reported sizes (769 MB and 619 MB) were measured at tag `q1`, before Redis was added in Q2. Run `git checkout q1` to rebuild them exactly.

## Question 2

```bash
docker compose up -d --build
curl -i -X POST localhost:8080/predict -H 'Content-Type: application/json' -d '{"text":"WIN a FREE iPhone now!"}'
./scripts/cache_benchmark.sh
docker compose down
```

The `X-Cache` response header shows `MISS` or `HIT`. The benchmark sends 20 distinct messages and then repeats them, and prints the average latency of each pass.

## Question 3

Start a two-node cluster with 2 allocatable CPUs per node. The Docker driver reports the host's cores as node capacity, so the extra kubelet setting reserves the rest:

```bash
minikube start --nodes 2 --cpus 2 --memory 2048 --driver=docker \
  --extra-config=kubelet.system-reserved=cpu=14
```

Then, from `q3-validation/`:

```bash
python generate_dataset.py
docker build -f Dockerfile.job -t shard-validator:v1 .
minikube image load shard-validator:v1
kubectl apply -f job.yaml
kubectl get pods -o wide
python collect_results.py --job-name shard-validation-job
```

The expected invalid-row counts for shards 0 to 7 are 3, 4, 5, 8, 5, 10, 12 and 4. Each pod waits 20 seconds (`HOLD_SECONDS`) so that the concurrent pods can be seen.

## Question 4

Version 1 is the API as of tag `q2`. Version 2 adds a version string to `/healthz`:

```bash
git checkout q2 && docker build -t spam-api:v1 . && git checkout main
docker build -t spam-api:v2 .
minikube image load spam-api:v1
minikube image load spam-api:v2

kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
curl http://$(minikube ip):30080/healthz

kubectl delete pod <pod-name>
kubectl get pods -l app=spam-api

kubectl set image deployment/spam-api api=spam-api:v2
kubectl rollout status deployment/spam-api
kubectl rollout history deployment/spam-api
```

`REDIS_HOST` is not set in the Deployment, so the API runs without the cache.

## AI disclosure

See `AI_DISCLOSURE.md`.
