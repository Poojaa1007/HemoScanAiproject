"""
HemoVision AI – Admin Routes
==============================
Admin dashboard with prediction statistics.
"""

from flask import Blueprint, render_template, jsonify
from routes.prediction import get_prediction_log
from services.model_service import get_metrics

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin_dashboard():
    """Render admin dashboard."""
    stats = _compute_stats()
    metrics = get_metrics()
    return render_template('admin.html', stats=stats, metrics=metrics)


@admin_bp.route('/api/admin/stats')
def admin_stats_api():
    """Return admin statistics as JSON."""
    stats = _compute_stats()
    metrics = get_metrics()
    return jsonify({
        'status': 'success',
        'data': {
            'prediction_stats': stats,
            'model_metrics': metrics
        }
    })


def _compute_stats():
    """Compute statistics from prediction log."""
    log = get_prediction_log()

    if not log:
        return {
            'total_predictions': 0,
            'severity_distribution': {'Normal': 0, 'Mild Anemia': 0, 'Moderate Anemia': 0, 'Severe Anemia': 0},
            'gender_distribution': {'Male': 0, 'Female': 0},
            'avg_hemoglobin': 0,
            'avg_confidence': 0
        }

    severity_dist = {}
    gender_dist = {'Male': 0, 'Female': 0}
    total_hb = 0
    total_conf = 0

    for entry in log:
        sev = entry['severity']
        severity_dist[sev] = severity_dist.get(sev, 0) + 1

        gender = 'Male' if entry['features']['gender'] == 0 else 'Female'
        gender_dist[gender] += 1

        total_hb += entry['features']['hemoglobin']
        total_conf += entry['confidence']

    n = len(log)
    return {
        'total_predictions': n,
        'severity_distribution': severity_dist,
        'gender_distribution': gender_dist,
        'avg_hemoglobin': round(total_hb / n, 2),
        'avg_confidence': round(total_conf / n, 1)
    }
