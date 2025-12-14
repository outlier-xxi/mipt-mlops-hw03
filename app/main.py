import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Body, FastAPI
from prometheus_client import Counter, Histogram, start_http_server
import time
from loguru import logger

from app.server.inference import ModelRunner


WINE_FEATURES_EXAMPLE = {
    "fixed acidity": 7.4,
    "volatile acidity": 0.70,
    "citric acid": 0.00,
    "residual sugar": 1.9,
    "chlorides": 0.076,
    "free sulfur dioxide": 11.0,
    "total sulfur dioxide": 34.0,
    "density": 0.9978,
    "pH": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4,
}


VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
MODEL_PATH = os.getenv("MODEL_PATH", "app/models/wine_quality_model.pkl")
SCALER_PATH = os.getenv("SCALER_PATH", "app/models/wine_scaler.pkl")

REQUEST_COUNT = Counter("predict_requests_total", "Total number of prediction requests")
LATENCY = Histogram("prediction_latency_seconds", "Model prediction latency (s)")
ERROR_COUNT = Counter("predict_errors_total", "Total number of prediction errors")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model at startup
    logger.info(f"Loading model from {MODEL_PATH} with scaler from {SCALER_PATH}")
    app.state.model_runner = ModelRunner(
        model_path=MODEL_PATH,
        version=VERSION,
        scaler_path=SCALER_PATH,
    )
    logger.info("Model loaded successfully")
    yield
    logger.info("Shutting down")


app = FastAPI(title="ML", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok","version": VERSION}

@app.post("/predict")
def predict(features: Annotated[dict[str, float], Body(examples=[WINE_FEATURES_EXAMPLE])]):
    start = time.time()
    REQUEST_COUNT.inc()
    try:
        model_runner: ModelRunner = app.state.model_runner
        prediction, confidence = model_runner.predict(features)

        latency = time.time() - start
        LATENCY.observe(latency)

        logger.info(f"Prediction successful: {prediction}, confidence: {confidence:.3f}, latency: {latency:.3f}s")
        return {
            "prediction": prediction,
            "confidence": confidence,
            "version": VERSION,
        }
    except Exception as e:
        ERROR_COUNT.inc()
        latency = time.time() - start
        LATENCY.observe(latency)
        logger.error(f"Prediction failed: {e}, latency: {latency:.3f}s")
        return {"error": str(e), "version": VERSION}


# Prometheus
start_http_server(8001)
