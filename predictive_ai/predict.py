
from pathlib import Path

import joblib
import pandas as pd

from features import extract_features

MODEL_PATH = Path(__file__).resolve().parent / "reading_difficulty_model.joblib"

saved = joblib.load(MODEL_PATH)
model = saved["model"]
feature_names = saved["features"]


def predict_difficulty(text):
    features = extract_features(text)

    X = pd.DataFrame([features])[feature_names]

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = {
        label: round(float(prob), 3)
        for label, prob in zip(model.classes_, probabilities)
    }

    return {
        "difficulty": prediction,
        "confidence": confidence,
        "features": features
    }


if __name__ == "__main__":
    sample = """
    The development of artificial intelligence involves
    sophisticated computational techniques and mathematical
    optimization procedures. These systems analyze complex
    patterns within large datasets and generate predictions
    based on previously observed relationships.
    """

    result = predict_difficulty(sample)

    print(result)
