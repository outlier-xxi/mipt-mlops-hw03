import joblib
import pandas as pd
from pathlib import Path
from typing import Optional
from loguru import logger


class ModelRunner:
    def __init__(self, model_path: str, version: str = "v1.0.0", scaler_path: Optional[str] = None):
        self.model = joblib.load(model_path)
        self.version = version
        self.scaler = joblib.load(scaler_path)
        logger.info(f"Loaded scaler from {scaler_path}")

    def predict(self, features: dict[str, float]) -> tuple[str, float]:
        # Convert features to DataFrame to preserve feature names and order
        df = pd.DataFrame([features])

        # Apply scaling
        df_scaled = pd.DataFrame(
            self.scaler.transform(df),
            columns=df.columns,
            index=df.index
        )
        prediction_input = df_scaled

        # Make prediction
        y = self.model.predict(prediction_input)[0]

        # Get confidence score from predict_proba if available
        try:
            proba = self.model.predict_proba(prediction_input)[0]
            # Return the maximum probability across all classes
            confidence = float(max(proba))
        except (AttributeError, Exception):
            # Model doesn't have predict_proba or failed
            confidence = 1.0

        return str(y), confidence