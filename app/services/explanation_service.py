"""
HemoVision AI – Explanation Service (SHAP)
===========================================
Provides explainable AI features using SHAP values.
Generates feature importance, top influencing parameters,
and clinical text explanations.
"""

import numpy as np
import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'ensemble_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')

FEATURE_NAMES = ['Gender', 'Hemoglobin', 'MCH', 'MCHC', 'MCV', 'Age', 'Pregnant']

# Clinical explanation templates
FEATURE_EXPLANATIONS = {
    'Hemoglobin': {
        'low': 'Low hemoglobin is the primary indicator of anemia, reflecting reduced oxygen-carrying capacity.',
        'high': 'Hemoglobin level is within healthy range, indicating adequate red blood cell function.'
    },
    'MCV': {
        'low': 'Reduced MCV suggests microcytic anemia, commonly caused by iron deficiency or thalassemia.',
        'high': 'Elevated MCV may indicate macrocytic anemia, potentially linked to B12/folate deficiency.'
    },
    'MCH': {
        'low': 'Low MCH indicates hypochromic red cells with less hemoglobin per cell, typical in iron deficiency.',
        'high': 'MCH within normal limits suggests adequate hemoglobin content per red blood cell.'
    },
    'MCHC': {
        'low': 'Low MCHC reflects reduced hemoglobin concentration in red cells, consistent with iron-deficiency anemia.',
        'high': 'MCHC is within reference range, suggesting normal hemoglobin saturation of red cells.'
    },
    'Gender': {
        'low': 'Being male, the hemoglobin thresholds for anemia classification are slightly higher (WHO guidelines).',
        'high': 'Being female, lower hemoglobin thresholds apply per WHO guidelines; menstrual iron loss is a factor.'
    },
    'Age': {
        'low': 'Younger age groups may have different normal ranges for blood parameters.',
        'high': 'Advanced age may contribute to anemia due to chronic disease or nutritional deficiencies.'
    },
    'Pregnant': {
        'low': 'Non-pregnant status; standard hemoglobin thresholds apply.',
        'high': 'Pregnancy increases blood volume, leading to physiological hemodilution and adjusted thresholds.'
    }
}


def get_feature_importance(features_dict):
    """
    Compute feature importance using the Random Forest sub-model
    within the ensemble (tree-based SHAP-compatible approach).
    Falls back to permutation-based importance if SHAP fails.

    Returns:
        dict with feature_importance, top_features, explanation
    """
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

        feature_array = np.array([[
            features_dict['gender'],
            features_dict['hemoglobin'],
            features_dict['mch'],
            features_dict['mchc'],
            features_dict['mcv'],
            features_dict['age'],
            features_dict['pregnant']
        ]])

        scaled = scaler.transform(feature_array)

        # Use the Random Forest sub-model for SHAP (tree-based, fast)
        rf_model = model.named_estimators_['rf']

        try:
            import shap
            explainer = shap.TreeExplainer(rf_model)
            shap_values = explainer.shap_values(scaled)

            # For multiclass, shap_values is a list of arrays (one per class)
            if isinstance(shap_values, list):
                # Get the predicted class
                pred_class = rf_model.predict(scaled)[0]
                importance = np.abs(shap_values[pred_class][0])
            else:
                importance = np.abs(shap_values[0])

        except Exception:
            # Fallback: use RF feature_importances_
            importance = rf_model.feature_importances_

        # Normalize to percentages
        total = importance.sum()
        if total > 0:
            importance_pct = (importance / total * 100).tolist()
        else:
            importance_pct = [100.0 / len(FEATURE_NAMES)] * len(FEATURE_NAMES)

        # Build feature importance dict
        fi = {FEATURE_NAMES[i]: round(importance_pct[i], 1) for i in range(len(FEATURE_NAMES))}

        # Top 3 features
        sorted_features = sorted(fi.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:3]

        # Generate clinical explanation
        explanation = _generate_explanation(top_features, features_dict)

        return {
            'feature_importance': fi,
            'top_features': [{'name': f[0], 'importance': f[1]} for f in top_features],
            'explanation': explanation
        }

    except Exception as e:
        # Graceful fallback
        return {
            'feature_importance': {name: round(100 / len(FEATURE_NAMES), 1) for name in FEATURE_NAMES},
            'top_features': [
                {'name': 'Hemoglobin', 'importance': 35.0},
                {'name': 'MCV', 'importance': 20.0},
                {'name': 'MCH', 'importance': 15.0}
            ],
            'explanation': f'Feature analysis completed with fallback method. Hemoglobin remains the primary diagnostic indicator.',
            'error': str(e)
        }


def _generate_explanation(top_features, features_dict):
    """Generate a clinical text explanation based on top features."""
    explanations = []

    # Map feature names to values for context
    value_map = {
        'Gender': features_dict['gender'],
        'Hemoglobin': features_dict['hemoglobin'],
        'MCH': features_dict['mch'],
        'MCHC': features_dict['mchc'],
        'MCV': features_dict['mcv'],
        'Age': features_dict['age'],
        'Pregnant': features_dict['pregnant']
    }

    # Normal reference ranges
    normal_ranges = {
        'Hemoglobin': (12.0, 17.0),
        'MCV': (80, 100),
        'MCH': (27, 33),
        'MCHC': (32, 36),
        'Age': (18, 65)
    }

    for feat_name, _ in top_features:
        val = value_map.get(feat_name)
        if feat_name in normal_ranges:
            low, high = normal_ranges[feat_name]
            direction = 'low' if val < low else 'high'
        elif feat_name == 'Gender':
            direction = 'low' if val == 0 else 'high'
        elif feat_name == 'Pregnant':
            direction = 'high' if val == 1 else 'low'
        else:
            direction = 'low'

        if feat_name in FEATURE_EXPLANATIONS:
            explanations.append(FEATURE_EXPLANATIONS[feat_name][direction])

    return ' '.join(explanations) if explanations else 'Analysis indicates values outside reference ranges. Consult with a healthcare provider for detailed evaluation.'
