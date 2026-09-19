import hashlib
import os

import joblib
import redis
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

MODEL_PATH = os.environ.get("MODEL_PATH", "data/model.joblib")
REDIS_HOST = os.environ.get("REDIS_HOST")
CACHE_TTL_SECONDS = 300

app = FastAPI()
model = None
cache = None


@app.on_event("startup")
def load_model():
    global model, cache
    model = joblib.load(MODEL_PATH)
    if REDIS_HOST:
        cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest, response: Response):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if cache is None:
        response.headers["X-Cache"] = "DISABLED"
        return {"label": model.predict([request.text])[0]}

    key = hashlib.sha256(request.text.encode()).hexdigest()
    cached = cache.get(key)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return {"label": cached}

    label = model.predict([request.text])[0]
    cache.setex(key, CACHE_TTL_SECONDS, label)
    response.headers["X-Cache"] = "MISS"
    return {"label": label}
