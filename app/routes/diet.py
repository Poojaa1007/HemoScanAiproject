"""
HemoVision AI – Diet Routes
==============================
Handles diet plan page rendering, API, and PDF export.
"""

from flask import Blueprint, request, jsonify, render_template, session, send_file
from services.diet_engine import get_diet_plan
import json
import io

diet_bp = Blueprint('diet', __name__)


@diet_bp.route('/diet')
def diet_page():
    """Render the diet plan page based on last prediction."""
    # Get data from session
    last_prediction = session.get('last_prediction')
    last_features = session.get('last_features')

    if last_prediction and last_features:
        result = json.loads(last_prediction)
        features = json.loads(last_features)
    else:
        # Default for direct access
        result = {'severity_level': 'Mild Anemia', 'severity_index': 1}
        features = {'gender': 1, 'hemoglobin': 11.0, 'pregnant': 0}

    severity = result.get('severity_level', 'Mild Anemia')
    gender = features.get('gender', 1)
    pregnant = features.get('pregnant', 0)
    budget_mode = request.args.get('budget', '0') == '1'

    # Generate all 3 severity plans for tabs
    plans = {}
    for sev in ['Mild Anemia', 'Moderate Anemia', 'Severe Anemia']:
        plans[sev] = get_diet_plan(sev, gender, pregnant, budget_mode)

    active_plan = plans.get(severity, plans['Mild Anemia'])

    return render_template('diet_plan.html',
                           plans=plans,
                           active_plan=active_plan,
                           severity=severity,
                           result=result,
                           features=features,
                           budget_mode=budget_mode)


@diet_bp.route('/api/diet')
def diet_api():
    """REST API for diet plan."""
    try:
        severity = request.args.get('severity', 'Mild Anemia')
        gender = int(request.args.get('gender', 1))
        pregnant = int(request.args.get('pregnant', 0))
        budget = request.args.get('budget', '0') == '1'

        plan = get_diet_plan(severity, gender, pregnant, budget)

        return jsonify({'status': 'success', 'data': plan})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@diet_bp.route('/diet/pdf')
def diet_pdf():
    """Generate and download diet plan as PDF."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        last_prediction = session.get('last_prediction')
        last_features = session.get('last_features')

        if last_prediction and last_features:
            result = json.loads(last_prediction)
            features = json.loads(last_features)
        else:
            result = {'severity_level': 'Mild Anemia'}
            features = {'gender': 1, 'hemoglobin': 11.0, 'pregnant': 0}

        severity = result.get('severity_level', 'Mild Anemia')
        plan = get_diet_plan(severity, features.get('gender', 1),
                             features.get('pregnant', 0))

        # Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     fontSize=18, textColor=colors.HexColor('#1a56db'),
                                     spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                       fontSize=14, textColor=colors.HexColor('#1e3a5f'),
                                       spaceBefore=15, spaceAfter=8)
        body_style = styles['Normal']

        elements = []

        # Title
        elements.append(Paragraph('HemoVision AI - Personalized Diet Plan', title_style))
        elements.append(Spacer(1, 10))

        # Patient Summary
        elements.append(Paragraph('Patient Summary', heading_style))
        summary_data = [
            ['Severity Level', severity],
            ['Hemoglobin', f"{features.get('hemoglobin', 'N/A')} g/dL"],
            ['Daily Iron Target', f"{plan['iron_target_mg']} mg"],
            ['Timeline', plan['hemoglobin_goal']['timeline']]
        ]
        summary_table = Table(summary_data, colWidths=[2.5 * inch, 3.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e3a5f')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c4d7f2')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 15))

        # Weekly Meal Plan
        elements.append(Paragraph('Weekly Meal Plan', heading_style))
        for day_plan in plan['weekly_plan']:
            elements.append(Paragraph(f"<b>{day_plan['day']}</b>", body_style))
            for meal_type, meal in day_plan['meals'].items():
                elements.append(Paragraph(
                    f"  {meal_type.capitalize()}: {meal['name']} ({meal['iron_mg']} mg iron)",
                    body_style))
            elements.append(Spacer(1, 6))

        # Absorption Tips
        elements.append(Paragraph('Iron Absorption Tips', heading_style))
        for tip in plan['absorption_tips']:
            elements.append(Paragraph(f"• {tip['tip']}", body_style))

        # Disclaimer
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            '<i>Disclaimer: This diet plan is generated by AI for educational purposes. '
            'Always consult a healthcare professional before making dietary changes.</i>',
            ParagraphStyle('Disclaimer', parent=body_style, fontSize=8,
                           textColor=colors.grey)))

        doc.build(elements)
        buffer.seek(0)

        return send_file(buffer, mimetype='application/pdf',
                         as_attachment=True,
                         download_name='HemoVision_Diet_Plan.pdf')

    except ImportError:
        return jsonify({'error': 'PDF generation requires reportlab. Install with: pip install reportlab'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
