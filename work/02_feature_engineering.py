"""
===============================================================================
02_FEATURE_ENGINEERING.PY
Search Intelligence Capstone — Feature Extraction & Label Definition
===============================================================================
This module extracts time-aware rolling window features from DuckDB and computes
search intelligence metrics: position decay slope, CTR deficit ratio, impression ratio,
and target opportunity labels (`needs_refresh`).
"""

import os
import json
import numpy as np
import pandas as pd
import duckdb

def compute_search_features(db_path="data/search_intelligence.duckdb", output_path="data/feature_matrix.parquet"):
    con = duckdb.connect(db_path, read_only=True)
    
    # Load baseline params
    params_path = "data/ctr_baseline_params.json"
    a_param, b_param = 0.32, -1.12
    if os.path.exists(params_path):
        with open(params_path, "r") as f:
            p = json.load(f)
            a_param, b_param = p["a"], p["b"]
            
    print(f"[Features] Loaded Baseline CTR Curve parameters: a={a_param:.4f}, b={b_param:.4f}")
    
    # Compute features via DuckDB SQL aggregations
    query = f"""
    WITH date_bounds AS (
        SELECT MAX(date) as max_date FROM search_performance
    ),
    aggregated AS (
        SELECT 
            sp.page_id,
            sp.archetype_ground_truth,
            
            -- Recent 7 days metrics (t-7 to t)
            AVG(CASE WHEN sp.date >= db.max_date - INTERVAL '7 days' THEN sp.position END) as pos_7d,
            SUM(CASE WHEN sp.date >= db.max_date - INTERVAL '7 days' THEN sp.impressions END) as imp_7d,
            SUM(CASE WHEN sp.date >= db.max_date - INTERVAL '7 days' THEN sp.clicks END) as clicks_7d,
            
            -- Mid 30 days metrics (t-30 to t)
            AVG(CASE WHEN sp.date >= db.max_date - INTERVAL '30 days' THEN sp.position END) as pos_30d,
            SUM(CASE WHEN sp.date >= db.max_date - INTERVAL '30 days' THEN sp.impressions END) as imp_30d,
            SUM(CASE WHEN sp.date >= db.max_date - INTERVAL '30 days' THEN sp.clicks END) as clicks_30d,
            
            -- Earlier baseline metrics (t-90 to t-30)
            AVG(CASE WHEN sp.date < db.max_date - INTERVAL '30 days' THEN sp.position END) as pos_historical,
            SUM(CASE WHEN sp.date < db.max_date - INTERVAL '30 days' THEN sp.impressions END) as imp_historical,
            SUM(CASE WHEN sp.date < db.max_date - INTERVAL '30 days' THEN sp.clicks END) as clicks_historical,
            
            -- Overall window metrics
            AVG(sp.position) as pos_90d,
            SUM(sp.impressions) as imp_90d,
            SUM(sp.clicks) as clicks_90d,
            STDDEV(sp.position) as pos_volatility_std,
            AVG(sp.query_count) as avg_query_count
            
        FROM search_performance sp, date_bounds db
        GROUP BY sp.page_id, sp.archetype_ground_truth
    )
    SELECT 
        page_id,
        archetype_ground_truth,
        
        pos_7d,
        pos_30d,
        pos_historical,
        pos_90d,
        
        imp_7d,
        imp_30d,
        imp_historical,
        imp_90d,
        
        clicks_7d,
        clicks_30d,
        clicks_historical,
        clicks_90d,
        
        -- Engineered Features
        (pos_30d - pos_historical) as pos_drift_30d_vs_hist,
        (pos_7d - pos_30d) as pos_drift_7d_vs_30d,
        
        (imp_30d * 1.0 / NULLIF(imp_historical / 2.0, 0)) as imp_ratio_30d_vs_hist,
        
        (clicks_30d * 1.0 / NULLIF(imp_30d, 0)) as ctr_observed_30d,
        
        pos_volatility_std,
        avg_query_count
        
    FROM aggregated;
    """
    
    df_feat = con.execute(query).df()
    con.close()
    
    # Vectorized post-processing in pandas/numpy
    # 1. Compute expected CTR based on empirical baseline curve
    df_feat['ctr_expected_30d'] = a_param * (df_feat['pos_30d'].clip(lower=1.0) ** b_param)
    df_feat['ctr_expected_30d'] = df_feat['ctr_expected_30d'].clip(upper=0.40)
    
    # 2. Compute CTR Deficit Ratio: (Expected - Observed) / Expected
    df_feat['ctr_deficit_ratio'] = (df_feat['ctr_expected_30d'] - df_feat['ctr_observed_30d']) / np.maximum(0.001, df_feat['ctr_expected_30d'])
    df_feat['ctr_deficit_ratio'] = df_feat['ctr_deficit_ratio'].clip(-1.0, 2.0)
    
    # 3. Traffic / Click Decay Velocity
    df_feat['click_decay_velocity'] = (df_feat['clicks_30d'] / 30.0) - (df_feat['clicks_historical'] / 60.0)
    
    # 4. Target Label definition (Needs Refresh Opportunity):
    # High opportunity if:
    # (a) Position drift >= 1.5 rank drop OR
    # (b) CTR Deficit Ratio >= 0.35 (observed CTR is 35%+ below baseline expectation for its position) OR
    # (c) Ground truth archetype is Decaying (1) or CTR Underperformer (2)
    df_feat['target_needs_refresh'] = np.where(
        (df_feat['pos_drift_30d_vs_hist'] >= 1.2) | 
        (df_feat['ctr_deficit_ratio'] >= 0.30) |
        (df_feat['archetype_ground_truth'].isin([1, 2])), 
        1, 0
    )
    
    # Clean NaNs/Infs
    df_feat.fillna(0, inplace=True)
    
    # Save to Parquet
    df_feat.to_parquet(output_path, index=False)
    print(f"[Features] Saved {len(df_feat)} engineered page feature vectors to {output_path}")
    print(f"[Label Balance] Needs Refresh: {df_feat['target_needs_refresh'].sum()} / {len(df_feat)} ({df_feat['target_needs_refresh'].mean()*100:.1f}%)")
    
    return df_feat

if __name__ == "__main__":
    compute_search_features()
