"""
===============================================================================
GENERATE_W07_PLAYBOOK.PY
Search Intelligence Capstone — Week 7 Action Playbook Generator
===============================================================================
This module constructs the w07_action_playbook.ipynb notebook, runs the complete
opportunity scoring engine, generates plots in work/figures/, exports the action
queue to work/outputs/, and exports metrics JSON.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set aesthetics for paper figures
plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def build_action_playbook():
    # Directories
    os.makedirs("work/notebooks", exist_ok=True)
    os.makedirs("work/outputs", exist_ok=True)
    os.makedirs("work/figures", exist_ok=True)
    os.makedirs("work/metrics", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 1. Load Feature Matrix or generate if not present
    feat_path = "data/feature_matrix.parquet"
    if not os.path.exists(feat_path):
        import importlib
        feat_module = importlib.import_module("work.02_feature_engineering")
        df = feat_module.compute_search_features()
    else:
        df = pd.read_parquet(feat_path)

    # 2. Compute Opportunity Scores and Reason Codes
    np.random.seed(42)
    
    # Calculate score (0-100) based on features
    df['opportunity_score'] = (
        (df['ctr_deficit_ratio'].clip(0, 1) * 45) +
        (df['pos_drift_30d_vs_hist'].clip(0, 5) / 5.0 * 35) +
        (np.log1p(df['imp_30d']) / np.log1p(df['imp_30d'].max()) * 20)
    ).round(1)

    recommendations = []
    reason_code_counts = {
        "DECAY_POSITION_SLIP": 0,
        "CTR_UNDERPERFORMING": 0,
        "HIGH_IMP_LOW_CLICK": 0,
        "MONITOR_VOLATILITY": 0,
        "STABLE_PERFORMER": 0
    }
    
    archetype_action_map = {
        0: "PROTECT_AND_MONITOR",
        1: "REWRITE_CONTENT_INTENT",
        2: "OPTIMIZE_METADATA_TITLES",
        3: "MONITOR_QUERY_INTENT"
    }

    for idx, row in df.iterrows():
        pos_drift = row['pos_drift_30d_vs_hist']
        ctr_deficit = row['ctr_deficit_ratio']
        pos_30d = row['pos_30d']
        imp_30d = row['imp_30d']
        archetype = int(row['archetype_ground_truth'])
        score = row['opportunity_score']
        
        reason_codes = []
        if pos_drift >= 1.2:
            reason_codes.append("DECAY_POSITION_SLIP")
            reason_code_counts["DECAY_POSITION_SLIP"] += 1
        if ctr_deficit >= 0.25:
            reason_codes.append("CTR_UNDERPERFORMING")
            reason_code_counts["CTR_UNDERPERFORMING"] += 1
        if imp_30d > 2000 and ctr_deficit >= 0.15:
            reason_codes.append("HIGH_IMP_LOW_CLICK")
            reason_code_counts["HIGH_IMP_LOW_CLICK"] += 1
        if row['pos_volatility_std'] > 2.0:
            reason_codes.append("MONITOR_VOLATILITY")
            reason_code_counts["MONITOR_VOLATILITY"] += 1
            
        if not reason_codes:
            reason_codes.append("STABLE_PERFORMER")
            reason_code_counts["STABLE_PERFORMER"] += 1

        # Determine Primary Recommended Action
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
            
        # Value / ROI recoverability index
        expected_recovered_clicks = int(imp_30d * max(0, ctr_deficit) * 0.5)

        recommendations.append({
            "page_id": row['page_id'],
            "opportunity_score": float(score),
            "archetype": archetype,
            "pos_30d": round(float(pos_30d), 1),
            "pos_drift": round(float(pos_drift), 2),
            "imp_30d": int(imp_30d),
            "clicks_30d": int(row['clicks_30d']),
            "ctr_observed_pct": round(float(row['ctr_observed_30d']) * 100, 2),
            "ctr_expected_pct": round(float(row['ctr_expected_30d']) * 100, 2),
            "ctr_deficit_pct": round(float(ctr_deficit) * 100, 1),
            "expected_recovered_clicks": expected_recovered_clicks,
            "reason_codes": ", ".join(reason_codes),
            "recommended_action": action,
            "urgency": urgency
        })

    df_rec = pd.DataFrame(recommendations)
    df_rec.sort_values(by="opportunity_score", ascending=False, inplace=True)
    df_rec['rank'] = range(1, len(df_rec) + 1)

    # 3. Export Action Queue & Recommendations
    csv_out = "work/outputs/ranked_action_queue.csv"
    json_out = "work/outputs/ranked_recommendations.json"
    data_json_out = "data/ranked_recommendations.json"
    
    df_rec.to_csv(csv_out, index=False)
    
    rec_dict = df_rec.to_dict(orient="records")
    with open(json_out, "w") as f:
        json.dump(rec_dict, f, indent=2)
    with open(data_json_out, "w") as f:
        json.dump(rec_dict, f, indent=2)

    print(f"[Exports] Exported action queue CSV to {csv_out}")
    print(f"[Exports] Exported recommendations JSON to {json_out}")

    # 4. Generate Figures in work/figures/
    
    # Figure 1: Reason Code Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    reason_series = pd.Series(reason_code_counts).sort_values(ascending=True)
    bars = ax.barh(reason_series.index, reason_series.values, color='#06b6d4', edgecolor='#0891b2')
    ax.set_title('Diagnostic Reason Code Frequency', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Number of Content Assets', fontsize=12)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 5, bar.get_y() + bar.get_height()/2, f"{int(w)}", ha='left', va='center', fontweight='bold')
    plt.tight_layout()
    fig1_path = "work/figures/reason_code_distribution.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # Figure 2: Opportunity Score Histogram
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df_rec['opportunity_score'], kde=True, color='#3b82f6', ax=ax, bins=25)
    ax.set_title('Distribution of Content Opportunity Scores (0-100)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Opportunity Score', fontsize=12)
    ax.set_ylabel('Page Count', fontsize=12)
    plt.tight_layout()
    fig2_path = "work/figures/opportunity_score_hist.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    # Figure 3: Archetype vs Action Matrix
    fig, ax = plt.subplots(figsize=(9, 5))
    ct = pd.crosstab(df_rec['archetype'], df_rec['recommended_action'])
    ct.index = ['Stable (0)', 'Decaying (1)', 'CTR Deficit (2)', 'Growing (3)']
    sns.heatmap(ct, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax, linewidths=1)
    ax.set_title('Archetype to Recommended Action Mapping Matrix', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Content Archetype', fontsize=12)
    ax.set_xlabel('Recommended Action Playbook', fontsize=12)
    plt.tight_layout()
    fig3_path = "work/figures/archetype_action_matrix.png"
    plt.savefig(fig3_path, dpi=300)
    plt.close()

    # Figure 4: ROI Cost-Value Matrix (Impressions vs CTR Deficit)
    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(
        df_rec['imp_30d'], 
        df_rec['ctr_deficit_pct'], 
        c=df_rec['opportunity_score'], 
        cmap='viridis', 
        alpha=0.8,
        edgecolors='none'
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Opportunity Score', fontsize=11)
    ax.set_title('Cost-Value Prioritization: Impression Volume vs CTR Deficit', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('30-Day Impression Volume', fontsize=12)
    ax.set_ylabel('CTR Deficit (%)', fontsize=12)
    plt.tight_layout()
    fig4_path = "work/figures/roi_cost_value_scatter.png"
    plt.savefig(fig4_path, dpi=300)
    plt.close()

    print("[Figures] Saved 4 publication figures to work/figures/")

    # 5. Export Metrics JSON
    playbook_metrics = {
        "total_pages_scored": len(df_rec),
        "critical_action_pages": int((df_rec['urgency'] == 'CRITICAL').sum()),
        "high_action_pages": int((df_rec['urgency'] == 'HIGH').sum()),
        "medium_action_pages": int((df_rec['urgency'] == 'MEDIUM').sum()),
        "low_action_pages": int((df_rec['urgency'] == 'LOW').sum()),
        "total_estimated_recoverable_clicks_monthly": int(df_rec['expected_recovered_clicks'].sum()),
        "reason_code_counts": reason_code_counts,
        "export_paths": {
            "queue_csv": csv_out,
            "recommendations_json": json_out,
            "figures": [fig1_path, fig2_path, fig3_path, fig4_path]
        }
    }
    
    with open("work/metrics/playbook_metrics.json", "w") as f:
        json.dump(playbook_metrics, f, indent=2)
    with open("data/playbook_metrics.json", "w") as f:
        json.dump(playbook_metrics, f, indent=2)

    print("[Metrics] Exported playbook metrics JSON to work/metrics/playbook_metrics.json")
    
    return playbook_metrics

if __name__ == "__main__":
    build_action_playbook()
