import os
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, start_http_server
import time
import random
from loguru import logger


app = FastAPI(title="ML")

REQUEST_COUNT = Counter("predict_requests_total", "Total number of prediction requests")
LATENCY = Histogram("prediction_latency_seconds", "Model prediction latency (s)")
ERROR_COUNT = Counter("predict_errors_total", "Total number of prediction errors")

VERSION = os.getenv("MODEL_VERSION", "v1.0.0")


@app.get("/health")
def health():
    return {"status": "ok","version": VERSION}

@app.get("/predict")
def predict():
    start = time.time()
    REQUEST_COUNT.inc()
    try:
        
        
        latency = time.time()-start
        LATENCY.observe(latency)

        logger.info(f"Prediction successful: latency: {latency:.3f}s")
        return {"prediction":"class_A","version":VERSION}
    except Exception as e:
        ERROR_COUNT.inc()
        latency = time.time()-start
        LATENCY.observe(latency)
        logger.error(f"Prediction failed: latency: {latency:.3f}s")
        return {"error": str(e), "version": VERSION}


# Prometheus
start_http_server(8001)
