import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, roc_auc_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report
)

def train_churn_prediction_models():
    """
    Trains and evaluates Scikit-learn Classification Models to predict Customer Churn.
    Follows ML Best Practices:
    - Train / Test split BEFORE scaling / encoding.
    - Multiple model comparison (Logistic Regression, Random Forest, Gradient Boosting).
    - Evaluation via ROC-AUC, F1-score, Precision, Recall, and Confusion Matrix.
    """
    print("\n========================================================")
    print("      BUILDING CHURN PREDICTION CLASSIFICATION PIPELINE  ")
    print("========================================================\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'src' else script_dir
    data_dir = os.path.join(project_root, 'data')

    data_path = os.path.join(data_dir, 'rfm_segmented_customers.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError("RFM segmented customer data missing. Run rfm_segmentation.py first.")

    df = pd.read_csv(data_path)

    # 1. Feature Engineering & Target Definition
    numeric_features = [
        'R_Score', 'F_Score', 'M_Score', 'rfm_total_score', 'monetary',
        'avg_order_value', 'total_items_purchased', 'avg_shipping_delay',
        'total_returns', 'avg_discount_rate', 'tenure_days',
        'support_tickets_opened', 'email_open_rate', 'app_installed'
    ]
    categorical_features = ['acquisition_channel', 'country', 'preferred_category']

    X = df[numeric_features + categorical_features]
    y = df['is_churned']

    # 2. Strict Train-Test Split (80% Train, 20% Test) BEFORE fitting preprocessors
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Data Split: Train Set = {len(X_train)} rows | Test Set = {len(X_test)} rows")
    print(f"Target Distribution in Train Set: {y_train.mean()*100:.2f}% Churned")
    print(f"Target Distribution in Test Set:  {y_test.mean()*100:.2f}% Churned\n")

    # 3. Create Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
        ]
    )

    # 4. Define Candidate Models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42)
    }

    results = {}
    best_model_name = None
    best_roc_auc = -1
    best_pipeline = None

    # 5. Train & Evaluate Models
    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])

        # Fit strictly on Training Data
        pipeline.fit(X_train, y_train)

        # Predict on Test Set
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_proba)
        f1 = f1_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)

        results[name] = {
            'Accuracy': acc,
            'ROC_AUC': roc_auc,
            'F1_Score': f1,
            'Precision': prec,
            'Recall': rec,
            'Pipeline': pipeline
        }

        print(f"--- Model: {name} ---")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  ROC-AUC:   {roc_auc:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}\n")

        if roc_auc > best_roc_auc:
            best_roc_auc = roc_auc
            best_model_name = name
            best_pipeline = pipeline

    print(f"[BEST MODEL] Best Performing Model: {best_model_name} with ROC-AUC = {best_roc_auc:.4f}")

    # 6. Detailed Evaluation of Winning Model
    y_pred_best = best_pipeline.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    print("\nConfusion Matrix (Best Model):")
    print(cm)
    print("\nClassification Report (Best Model):")
    print(classification_report(y_test, y_pred_best))

    # 7. Save Churn Risk Predictions for All Customers
    df['churn_probability'] = best_pipeline.predict_proba(X)[:, 1]
    df['predicted_churn_status'] = best_pipeline.predict(X)
    df['risk_tier'] = pd.cut(
        df['churn_probability'],
        bins=[0.0, 0.30, 0.60, 1.0],
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )

    output_path = os.path.join('data', 'churn_predictions.csv')
    df.to_csv(output_path, index=False)
    print(f"\nFull customer churn predictions saved to: {output_path}")

    return results, best_model_name, best_roc_auc, results[best_model_name]['F1_Score']

if __name__ == "__main__":
    train_churn_prediction_models()
