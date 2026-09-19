import os

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = os.environ.get("MODEL_PATH", "data/model.joblib")

app = FastAPI()
model = None


@app.on_event("startup")
def load_model():
    global model
    model = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    return {"label": model.predict([request.text])[0]}
