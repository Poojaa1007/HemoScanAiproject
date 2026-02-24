"""
HemoVision AI – Model Training Script
======================================
Generates synthetic anemia dataset based on WHO clinical parameters,
trains an Ensemble VotingClassifier (LR, RF, GBM, SVM),
and saves the model + scaler for production use.
"""

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

np.random.seed(42)

# ─── Generate Synthetic Dataset Based on WHO Parameters ───────────────────────
def generate_dataset(n_samples=3000):
    """
    Generate a synthetic anemia dataset with realistic clinical distributions.
    Classes:
        0 = Normal
        1 = Mild Anemia
        2 = Moderate Anemia
        3 = Severe Anemia
    Features: Gender, Hemoglobin, MCH, MCHC, MCV, Age, Pregnancy
    """
    records = []

    for _ in range(n_samples):
        gender = np.random.choice([0, 1])  # 0=Male, 1=Female
        age = np.random.randint(5, 85)
        pregnant = 1 if (gender == 1 and 18 <= age <= 45 and np.random.random() < 0.15) else 0

        # Decide severity class with realistic prevalence
        severity = np.random.choice([0, 1, 2, 3], p=[0.45, 0.28, 0.18, 0.09])

        # WHO hemoglobin thresholds (g/dL) by class
        if severity == 0:  # Normal
            if gender == 0:
                hb = np.random.normal(15.0, 1.2)
            elif pregnant:
                hb = np.random.normal(12.5, 0.8)
            else:
                hb = np.random.normal(13.5, 1.0)
        elif severity == 1:  # Mild
            if gender == 0:
                hb = np.random.normal(11.5, 0.8)
            elif pregnant:
                hb = np.random.normal(10.5, 0.6)
            else:
                hb = np.random.normal(11.0, 0.7)
        elif severity == 2:  # Moderate
            hb = np.random.normal(8.5, 0.8)
        else:  # Severe
            hb = np.random.normal(6.0, 1.0)

        hb = max(3.0, min(hb, 20.0))

        # Correlated blood indices
        if severity == 0:
            mcv = np.random.normal(88, 4)
            mch = np.random.normal(30, 2)
            mchc = np.random.normal(34, 1)
        elif severity == 1:
            mcv = np.random.normal(78, 6)
            mch = np.random.normal(26, 3)
            mchc = np.random.normal(32, 1.5)
        elif severity == 2:
            mcv = np.random.normal(70, 7)
            mch = np.random.normal(22, 3)
            mchc = np.random.normal(30, 2)
        else:
            mcv = np.random.normal(62, 8)
            mch = np.random.normal(18, 3)
            mchc = np.random.normal(28, 2)

        mcv = max(50, min(mcv, 110))
        mch = max(12, min(mch, 40))
        mchc = max(24, min(mchc, 38))

        records.append([gender, hb, mch, mchc, mcv, age, pregnant, severity])

    columns = ['Gender', 'Hemoglobin', 'MCH', 'MCHC', 'MCV', 'Age', 'Pregnant', 'Severity']
    return pd.DataFrame(records, columns=columns)


def train_and_save():
    """Train the ensemble model and save artifacts."""
    print("=" * 60)
    print("  HemoVision AI – Model Training Pipeline")
    print("=" * 60)

    # Generate data
    print("\n[1/5] Generating synthetic clinical dataset...")
    df = generate_dataset(3000)
    print(f"  Dataset shape: {df.shape}")
    print(f"  Class distribution:\n{df['Severity'].value_counts().sort_index().to_string()}")

    X = df.drop('Severity', axis=1)
    y = df['Severity']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    print("\n[2/5] Fitting StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Build ensemble
    print("\n[3/5] Building Ensemble VotingClassifier...")
    estimators = [
        ('lr', LogisticRegression(max_iter=1000, random_state=42, C=1.0)),
        ('rf', RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42)),
        ('svm', SVC(probability=True, kernel='rbf', random_state=42, C=1.0))
    ]
    ensemble = VotingClassifier(estimators=estimators, voting='soft')

    # Cross-validation
    print("\n[4/5] Running 5-fold cross-validation...")
    cv_scores = cross_val_score(ensemble, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Train final model
    print("\n[5/5] Training final ensemble model...")
    ensemble.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = ensemble.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Test Accuracy: {accuracy:.4f}")
    print(f"\n  Classification Report:\n{classification_report(y_test, y_pred, target_names=['Normal', 'Mild', 'Moderate', 'Severe'])}")
    print(f"  Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

    # Save artifacts
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, 'ensemble_model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    metrics_path = os.path.join(models_dir, 'metrics.pkl')

    joblib.dump(ensemble, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump({
        'accuracy': float(accuracy),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }, metrics_path)

    print(f"\n✅ Model saved to: {model_path}")
    print(f"✅ Scaler saved to: {scaler_path}")
    print(f"✅ Metrics saved to: {metrics_path}")
    print("=" * 60)


if __name__ == '__main__':
    train_and_save()
