"""
HemoVision AI – Prediction Routes
===================================
Handles both web form submissions and REST API predictions.
"""

from flask import Blueprint, request, jsonify, render_template, session
from services.model_service import predict, get_metrics
from services.explanation_service import get_feature_importance
import json

prediction_bp = Blueprint('prediction', __name__)

# ─── In-Memory Prediction Log (lightweight; replace with SQLite for production) ─
prediction_log = []


@prediction_bp.route('/predict', methods=['POST'])
def predict_form():
    """Handle form-based prediction and render result page."""
    try:
        features = _extract_features(request.form)
        result = predict(features)
        explanation = get_feature_importance(features)

        # Merge explanation into result
        result['feature_importance'] = explanation['feature_importance']
        result['top_features'] = explanation['top_features']
        result['explanation'] = explanation['explanation']

        # Log prediction
        prediction_log.append({
            'features': features,
            'severity': result['severity_level'],
            'confidence': result['confidence_score']
        })

        # Store in session for diet page
        session['last_prediction'] = json.dumps(result, default=str)
        session['last_features'] = json.dumps(features)

        return render_template('result.html', result=result, features=features)

    except Exception as e:
        return render_template('index.html', error=str(e))


@prediction_bp.route('/api/predict', methods=['POST'])
def predict_api():
    """REST API endpoint for prediction."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        features = _extract_features_json(data)
        result = predict(features)
        explanation = get_feature_importance(features)

        result['feature_importance'] = explanation['feature_importance']
        result['top_features'] = explanation['top_features']
        result['explanation'] = explanation['explanation']

        # Log prediction
        prediction_log.append({
            'features': features,
            'severity': result['severity_level'],
            'confidence': result['confidence_score']
        })

        return jsonify({
            'status': 'success',
            'data': result
        })

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


@prediction_bp.route('/api/metrics', methods=['GET'])
def api_metrics():
    """Return model performance metrics."""
    metrics = get_metrics()
    if metrics:
        return jsonify({'status': 'success', 'data': metrics})
    return jsonify({'status': 'error', 'message': 'Metrics not available'}), 404


def get_prediction_log():
    """Return the prediction log for admin use."""
    return prediction_log


def _extract_features(form_data):
    """Extract and validate features from form data."""
    try:
        features = {
            'gender': int(form_data.get('gender', 0)),
            'hemoglobin': float(form_data.get('hemoglobin', 0)),
            'mch': float(form_data.get('mch', 0)),
            'mchc': float(form_data.get('mchc', 0)),
            'mcv': float(form_data.get('mcv', 0)),
            'age': int(form_data.get('age', 0)),
            'pregnant': int(form_data.get('pregnant', 0))
        }
    except (ValueError, TypeError) as e:
        raise ValueError(f'Invalid input data: {e}')

    _validate_features(features)
    return features


def _extract_features_json(data):
    """Extract and validate features from JSON data."""
    required = ['gender', 'hemoglobin', 'mch', 'mchc', 'mcv', 'age', 'pregnant']
    for field in required:
        if field not in data:
            raise ValueError(f'Missing required field: {field}')

    features = {
        'gender': int(data['gender']),
        'hemoglobin': float(data['hemoglobin']),
        'mch': float(data['mch']),
        'mchc': float(data['mchc']),
        'mcv': float(data['mcv']),
        'age': int(data['age']),
        'pregnant': int(data['pregnant'])
    }

    _validate_features(features)
    return features


def _validate_features(features):
    """Validate feature ranges."""
    if features['hemoglobin'] < 2 or features['hemoglobin'] > 25:
        raise ValueError('Hemoglobin must be between 2 and 25 g/dL')
    if features['age'] < 1 or features['age'] > 120:
        raise ValueError('Age must be between 1 and 120')
    if features['mcv'] < 40 or features['mcv'] > 120:
        raise ValueError('MCV must be between 40 and 120 fL')
    if features['mch'] < 10 or features['mch'] > 45:
        raise ValueError('MCH must be between 10 and 45 pg')
    if features['mchc'] < 20 or features['mchc'] > 42:
        raise ValueError('MCHC must be between 20 and 42 g/dL')
    if features['gender'] not in [0, 1]:
        raise ValueError('Gender must be 0 (Male) or 1 (Female)')
    if features['pregnant'] not in [0, 1]:
        raise ValueError('Pregnancy status must be 0 or 1')
