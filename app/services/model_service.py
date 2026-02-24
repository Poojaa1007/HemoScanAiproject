"""
HemoVision AI – Model Service
==============================
Loads the trained ensemble model and scaler once at startup.
Provides prediction with WHO-based severity classification,
confidence scoring, and clinical recommendations.
"""

import os
import joblib
import numpy as np

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'ensemble_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')
METRICS_PATH = os.path.join(BASE_DIR, 'models', 'metrics.pkl')

# ─── Singleton Model Loader ──────────────────────────────────────────────────
_model = None
_scaler = None
_metrics = None

SEVERITY_LABELS = ['Normal', 'Mild Anemia', 'Moderate Anemia', 'Severe Anemia']
FEATURE_NAMES = ['Gender', 'Hemoglobin', 'MCH', 'MCHC', 'MCV', 'Age', 'Pregnant']


def load_model():
    """Load model, scaler, and metrics into memory (singleton)."""
    global _model, _scaler, _metrics
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        if os.path.exists(METRICS_PATH):
            _metrics = joblib.load(METRICS_PATH)
    return _model, _scaler


def get_metrics():
    """Return saved model metrics."""
    global _metrics
    if _metrics is None:
        load_model()
    return _metrics


def who_severity(hemoglobin, gender, pregnant):
    """
    WHO hemoglobin-based anemia classification (g/dL).
    Men:      Normal ≥ 13, Mild 11–12.9, Moderate 8–10.9, Severe < 8
    Women:    Normal ≥ 12, Mild 11–11.9, Moderate 8–10.9, Severe < 8
    Pregnant: Normal ≥ 11, Mild 10–10.9, Moderate 7–9.9,  Severe < 7
    """
    if pregnant:
        if hemoglobin >= 11:
            return 0
        elif hemoglobin >= 10:
            return 1
        elif hemoglobin >= 7:
            return 2
        else:
            return 3
    elif gender == 0:  # Male
        if hemoglobin >= 13:
            return 0
        elif hemoglobin >= 11:
            return 1
        elif hemoglobin >= 8:
            return 2
        else:
            return 3
    else:  # Female
        if hemoglobin >= 12:
            return 0
        elif hemoglobin >= 11:
            return 1
        elif hemoglobin >= 8:
            return 2
        else:
            return 3


def get_recommendation(severity_idx, pregnant):
    """Return clinical recommendation based on severity."""
    recommendations = {
        0: "Your blood parameters are within normal range. Maintain a balanced diet rich in iron and vitamins. Schedule routine annual check-ups.",
        1: "Mild anemia detected. Increase dietary iron intake through leafy greens, legumes, and fortified cereals. Consider vitamin C to enhance absorption. Follow up in 4-6 weeks.",
        2: "Moderate anemia detected. Consult a healthcare provider promptly. Oral iron supplementation (ferrous sulfate 325mg daily) is recommended. Diagnostic workup for underlying causes advised.",
        3: "Severe anemia detected. Seek immediate medical attention. Parenteral iron therapy or blood transfusion may be required. Hospitalization should be considered."
    }
    rec = recommendations.get(severity_idx, recommendations[0])
    if pregnant and severity_idx > 0:
        rec += " MATERNAL ALERT: Anemia during pregnancy increases risk of preterm birth and low birth weight. Close obstetric monitoring is essential."
    return rec


def predict(features_dict):
    """
    Run prediction pipeline.

    Args:
        features_dict: {gender, hemoglobin, mch, mchc, mcv, age, pregnant}

    Returns:
        dict with severity_level, confidence_score, recommendation,
        who_classification, feature_values
    """
    model, scaler = load_model()

    # Build feature array in correct order
    feature_array = np.array([[
        features_dict['gender'],
        features_dict['hemoglobin'],
        features_dict['mch'],
        features_dict['mchc'],
        features_dict['mcv'],
        features_dict['age'],
        features_dict['pregnant']
    ]])

    # Scale and predict
    scaled = scaler.transform(feature_array)
    prediction = model.predict(scaled)[0]
    probabilities = model.predict_proba(scaled)[0]
    confidence = float(np.max(probabilities))

    # WHO cross-check
    who_class = who_severity(
        features_dict['hemoglobin'],
        features_dict['gender'],
        features_dict['pregnant']
    )

    # Use the more severe classification between AI and WHO
    final_severity = max(int(prediction), who_class)

    recommendation = get_recommendation(final_severity, features_dict['pregnant'])

    return {
        'severity_level': SEVERITY_LABELS[final_severity],
        'severity_index': final_severity,
        'confidence_score': round(confidence * 100, 1),
        'probabilities': {SEVERITY_LABELS[i]: round(float(p) * 100, 1) for i, p in enumerate(probabilities)},
        'recommendation': recommendation,
        'who_classification': SEVERITY_LABELS[who_class],
        'ai_classification': SEVERITY_LABELS[int(prediction)],
        'feature_values': features_dict,
        'feature_names': FEATURE_NAMES
    }
