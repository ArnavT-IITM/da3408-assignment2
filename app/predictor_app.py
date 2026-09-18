"""
predictor_app.py — AI Operations (AIOps), Module 3 Lecture 2b
FastAPI predictor implementing the KServe V1 inference protocol.
"""
import os, socket, time
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = os.environ.get("MODEL_PATH", "data/model.joblib")
POD_NAME = os.environ.get("POD_NAME", socket.gethostname())
NODE_NAME = os.environ.get("NODE_NAME", "unknown")

app = FastAPI(title="RF Classifier Predictor")
_bundle = None


@app.on_event("startup")
def load_model():
    global _bundle
    _bundle = joblib.load(MODEL_PATH)
    print(f"Loaded model ({len(_bundle['feature_columns'])} features) on pod={POD_NAME} node={NODE_NAME}")


class PredictRequest(BaseModel):
    instances: list[list[float]]


@app.get("/healthz")
def healthz():
    return {"status": "ok", "pod": POD_NAME, "node": NODE_NAME}


@app.get("/v1/models/{model_name}")
def model_ready(model_name: str):
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    return {"name": model_name, "ready": True}


@app.post("/v1/models/{model_name}:predict")
def predict(model_name: str, request: PredictRequest):
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    model = _bundle["model"]
    expected = len(_bundle["feature_columns"])
    for row in request.instances:
        if len(row) != expected:
            raise HTTPException(status_code=400, detail=f"Expected {expected} features, got {len(row)}")

    t0 = time.time()
    predictions = model.predict(request.instances).tolist()
    latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "predictions": predictions,
        "served_by_pod": POD_NAME,
        "served_by_node": NODE_NAME,
        "latency_ms": latency_ms,
    }
