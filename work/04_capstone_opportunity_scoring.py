"""
===============================================================================
04_CAPSTONE_OPPORTUNITY_SCORING.PY
Search Intelligence Capstone — Content Opportunity Scoring Engine
===============================================================================
This module applies the trained champion ML model to generate continuous
opportunity scores (0-100), automated diagnostic reason codes, and actionable
content playbooks. Results are exported to data/ranked_recommendations.json.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

def generate_opportunity_engine(feature_path="data/feature_matrix.parquet", output_json="data/ranked_recommendations.json"):
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
    
    # Train final production model
    clf = HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42)
    clf.fit(X, y)
    
    # Calculate refresh opportunity probabilities (0 to 100)
    probs = clf.predict_proba(X)[:, 1]
    df['opportunity_score'] = (probs * 100).round(1)
    
    # Assign Diagnostic Reason Codes & Action Recommendations
    recommendations = []
    
    for idx, row in df.iterrows():
        score = row['opportunity_score']
        pos_drift = row['pos_drift_30d_vs_hist']
        ctr_deficit = row['ctr_deficit_ratio']
        pos_30d = row['pos_30d']
        imp_30d = row['imp_30d']
        
        reason_codes = []
        
        if pos_drift >= 1.5:
            reason_codes.append("DECAY_POSITION_SLIP")
        if ctr_deficit >= 0.35:
            reason_codes.append("CTR_UNDERPERFORMING")
        if imp_30d > 2500 and ctr_deficit >= 0.20:
            reason_codes.append("HIGH_IMP_LOW_CLICK")
        if row['pos_volatility_std'] > 2.5:
            reason_codes.append("MONITOR_VOLATILITY")
            
        if not reason_codes:
            if score < 30.0:
                reason_codes.append("STABLE_PERFORMER")
            else:
                reason_codes.append("MODERATE_DECAY_RISK")
                
        # Primary Action Recommendation
        if "DECAY_POSITION_SLIP" in reason_codes and "CTR_UNDERPERFORMING" in reason_codes:
            action = "REWRITE_AND_UPDATE_METADATA"
            urgency = "CRITICAL"
        elif "DECAY_POSITION_SLIP" in reason_codes:
            action = "REWRITE_CONTENT_INTENT"
            urgency = "HIGH"
        elif "CTR_UNDERPERFORMING" in reason_codes or "HIGH_IMP_LOW_CLICK" in reason_codes:
            action = "OPTIMIZE_METADATA_TITLES"
            urgency = "HIGH"
        elif "MONITOR_VOLATILITY" in reason_codes:
            action = "MONITOR_QUERY_INTENT"
            urgency = "MEDIUM"
        else:
            action = "PROTECT_AND_MONITOR"
            urgency = "LOW"
            
        recommendations.append({
            "rank": 0, # To be sorted
            "page_id": row['page_id'],
            "opportunity_score": float(score),
            "pos_30d": round(float(pos_30d), 1),
            "pos_drift": round(float(pos_drift), 2),
            "imp_30d": int(imp_30d),
            "clicks_30d": int(row['clicks_30d']),
            "ctr_observed": round(float(row['ctr_observed_30d']) * 100, 2),
            "ctr_expected": round(float(row['ctr_expected_30d']) * 100, 2),
            "ctr_deficit_pct": round(float(ctr_deficit) * 100, 1),
            "reason_codes": reason_codes,
            "recommended_action": action,
            "urgency": urgency
        })
        
    # Sort recommendations by opportunity score descending
    recommendations.sort(key=lambda x: x['opportunity_score'], reverse=True)
    for r_idx, item in enumerate(recommendations):
        item['rank'] = r_idx + 1
        
    with open(output_json, "w") as f:
        json.dump(recommendations, f, indent=2)
        
    print(f"[Scoring Engine] Generated {len(recommendations)} ranked page recommendations in {output_json}")
    
    # Print Top 5 Opportunity Pages
    print("\n--- TOP 5 CONTENT REFRESH OPPORTUNITY PAGES ---")
    for item in recommendations[:5]:
        print(f"Rank #{item['rank']} | {item['page_id']} | Score: {item['opportunity_score']}/100 | Action: {item['recommended_action']} | Reasons: {', '.join(item['reason_codes'])}")
        
    return recommendations

if __name__ == "__main__":
    generate_opportunity_engine()
