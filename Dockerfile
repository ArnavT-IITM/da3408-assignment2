FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
COPY app/requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app/predictor_app.py app/
COPY data/model.joblib data/

ENV PATH="/opt/venv/bin:$PATH"
ENV MODEL_PATH=/app/data/model.joblib

EXPOSE 8080
CMD ["uvicorn", "app.predictor_app:app", "--host", "0.0.0.0", "--port", "8080"]
