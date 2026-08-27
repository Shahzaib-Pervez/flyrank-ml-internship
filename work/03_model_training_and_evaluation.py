"""
===============================================================================
03_MODEL_TRAINING_AND_EVALUATION.PY
Search Intelligence Capstone — Model Training, Cross-Validation & Evaluation
===============================================================================
This module evaluates ML classifiers against rule-based baselines using leak-free
cross-validation. It outputs quantitative performance metrics, confusion matrices,
and feature importance rankings.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, f1_score, precision_score, recall_score, confusion_matrix

def evaluate_models(feature_path="data/feature_matrix.parquet", output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_parquet(feature_path)
    
    feature_cols = [
        'pos_7d', 'pos_30d', 'pos_historical', 'pos_90d',
        'imp_7d', 'imp_30d', 'imp_historical', 'imp_90d',
        'clicks_7d', 'clicks_30d', 'clicks_90d',
        'pos_drift_30d_vs_hist', 'pos_drift_7d_vs_30d',
        'imp_ratio_30d_vs_hist', 'ctr_observed_30d',
        'ctr_expected_30d', 'ctr_deficit_ratio',
        'click_decay_velocity', 'pos_volatility_std', 'avg_query_count'
    ]
    
    X = df[feature_cols]
    y = df['target_needs_refresh']
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    models = {
        "Rule_Based_Baseline": "rule",
        "Logistic_Regression": Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(random_state=42))]),
        "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Hist_Gradient_Boosting": HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n[Evaluating] {name}...")
        
        y_true_all = []
        y_pred_all = []
        y_prob_all = []
        
        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            if name == "Rule_Based_Baseline":
                # Rule heuristic: position drift >= 1.0 or CTR deficit >= 0.25
                preds = ((X_val['pos_drift_30d_vs_hist'] >= 1.0) | (X_val['ctr_deficit_ratio'] >= 0.25)).astype(int)
                probs = np.where(X_val['ctr_deficit_ratio'] > 0, X_val['ctr_deficit_ratio'].clip(0, 1), 0.1)
            else:
                model.fit(X_train, y_train)
                preds = model.predict(X_val)
                probs = model.predict_proba(X_val)[:, 1]
                
            y_true_all.extend(y_val)
            y_pred_all.extend(preds)
            y_prob_all.extend(probs)
            
        y_true_all = np.array(y_true_all)
        y_pred_all = np.array(y_pred_all)
        y_prob_all = np.array(y_prob_all)
        
        # Calculate evaluation metrics
        roc_val = roc_auc_score(y_true_all, y_prob_all)
        p, r, _ = precision_recall_curve(y_true_all, y_prob_all)
        pr_auc_val = auc(r, p)
        f1_val = f1_score(y_true_all, y_pred_all)
        prec_val = precision_score(y_true_all, y_pred_all)
        rec_val = recall_score(y_true_all, y_pred_all)
        cm = confusion_matrix(y_true_all, y_pred_all).tolist()
        
        results[name] = {
            "ROC_AUC": round(float(roc_val), 4),
            "PR_AUC": round(float(pr_auc_val), 4),
            "F1_Score": round(float(f1_val), 4),
            "Precision": round(float(prec_val), 4),
            "Recall": round(float(rec_val), 4),
            "Confusion_Matrix": cm
        }
        
        print(f"   ROC-AUC: {roc_val:.4f} | PR-AUC: {pr_auc_val:.4f} | F1: {f1_val:.4f} | Precision: {prec_val:.4f} | Recall: {rec_val:.4f}")
        
    # Fit final champion model (HistGradientBoosting) on full dataset to get feature importances & scoring predictions
    final_model = HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42)
    final_model.fit(X, y)
    
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf_model.fit(X, y)
    
    importances = dict(zip(feature_cols, rf_model.feature_importances_))
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    
    # Save evaluation outputs to JSON
    with open(os.path.join(output_dir, "evaluation_metrics.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    with open(os.path.join(output_dir, "feature_importances.json"), "w") as f:
        json.dump(sorted_importances, f, indent=2)
        
    print(f"\n[Model Training Complete] Saved evaluation metrics & feature importances to {output_dir}")
    return results, sorted_importances

if __name__ == "__main__":
    evaluate_models()
