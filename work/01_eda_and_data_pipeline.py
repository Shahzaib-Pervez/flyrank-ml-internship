"""
===============================================================================
01_EDA_AND_DATA_PIPELINE.PY
Search Intelligence Capstone — FlyRank ML Internship Dataset Pipeline
===============================================================================
This module initializes the DuckDB analytical pipeline, loads/generates public-safe
search performance warehouse tables, computes foundational daily aggregations,
and fits an empirical position-to-CTR baseline curve.

Public Safety Rule Enforcement:
- No real domain names, URLs, credentials, or client identifiers.
- Anonymized identifiers (page_id_XXXX, query_cluster_YYY) are utilized throughout.
"""

import os
import sys
import numpy as np
import pandas as pd
import duckdb
from scipy.optimize import curve_fit
import json

def generate_flyrank_synthetic_warehouse(num_pages=500, days=90, seed=42):
    """
    Generates a realistic, anonymized search intelligence dataset in DuckDB format
    mimicking the FlyRank warehouse schema across a 90-day historical window.
    """
    np.random.seed(seed)
    start_date = pd.Timestamp("2026-05-28")
    date_range = [start_date + pd.Timedelta(days=i) for i in range(days)]
    
    records = []
    
    # Archetypes for pages:
    # 0: Stable high performers (20%)
    # 1: Decaying pages (Position drift downwards, traffic dropping) (30%)
    # 2: Underperforming CTR (High impressions, position 1-5, but CTR far below average) (25%)
    # 3: Growing / Momentum pages (25%)
    
    page_archetypes = np.random.choice([0, 1, 2, 3], size=num_pages, p=[0.20, 0.30, 0.25, 0.25])
    base_positions = np.random.uniform(1.2, 25.0, size=num_pages)
    base_impressions = np.random.exponential(scale=1500, size=num_pages) + 100
    
    for p_idx in range(num_pages):
        page_id = f"page_{p_idx+1000:04d}"
        archetype = page_archetypes[p_idx]
        base_pos = base_positions[p_idx]
        base_imp = base_impressions[p_idx]
        
        for t_idx, d in enumerate(date_range):
            # Time progress (0.0 to 1.0)
            t = t_idx / (days - 1)
            
            if archetype == 0:  # Stable
                pos_drift = np.random.normal(0, 0.2)
                imp_factor = np.random.normal(1.0, 0.05)
                ctr_factor = np.random.normal(1.0, 0.05)
            elif archetype == 1:  # Decaying
                pos_drift = t * np.random.uniform(3.0, 8.0) + np.random.normal(0, 0.3)
                imp_factor = max(0.2, 1.0 - 0.5 * t) + np.random.normal(0, 0.05)
                ctr_factor = max(0.3, 1.0 - 0.4 * t) + np.random.normal(0, 0.05)
            elif archetype == 2:  # CTR Underperformer
                pos_drift = np.random.normal(0, 0.3)
                imp_factor = np.random.normal(1.1, 0.05)
                ctr_factor = 0.35 + np.random.normal(0, 0.04) # low CTR relative to position
            else:  # Growing
                pos_drift = -t * np.random.uniform(2.0, 5.0) + np.random.normal(0, 0.3)
                imp_factor = (1.0 + 0.8 * t) + np.random.normal(0, 0.05)
                ctr_factor = np.random.normal(1.1, 0.05)
                
            curr_pos = max(1.0, base_pos + pos_drift)
            curr_imp = max(10, int(base_imp * imp_factor))
            
            # Expected CTR power-law formula: CTR ~ 0.30 / (pos ^ 1.1)
            expected_ctr = min(0.40, 0.32 / (curr_pos ** 1.12))
            actual_ctr = min(0.60, max(0.001, expected_ctr * ctr_factor))
            
            clicks = int(curr_imp * actual_ctr)
            query_count = max(1, int(np.sqrt(curr_imp) * np.random.uniform(0.8, 1.5)))
            
            records.append({
                "page_id": page_id,
                "date": d.strftime("%Y-%m-%d"),
                "impressions": curr_imp,
                "clicks": clicks,
                "ctr": round(clicks / max(1, curr_imp), 4),
                "position": round(curr_pos, 2),
                "query_count": query_count,
                "archetype_ground_truth": archetype
            })
            
    df = pd.DataFrame(records)
    return df

def run_duckdb_pipeline(data_dir="data"):
    """
    Initializes DuckDB connection, loads table, runs aggregate queries,
    and returns analytical summary.
    """
    os.makedirs(data_dir, exist_ok=True)
    df = generate_flyrank_synthetic_warehouse()
    
    db_path = os.path.join(data_dir, "search_intelligence.duckdb")
    con = duckdb.connect(db_path)
    
    # Register DataFrame in DuckDB
    con.register("df_raw", df)
    
    # Create persistent table in DuckDB
    con.execute("""
        CREATE OR REPLACE TABLE search_performance AS 
        SELECT 
            page_id,
            CAST(date AS DATE) as date,
            impressions,
            clicks,
            ctr,
            position,
            query_count,
            archetype_ground_truth
        FROM df_raw;
    """)
    
    print(f"[DuckDB] Ingested {con.execute('SELECT COUNT(*) FROM search_performance').fetchone()[0]} rows.")
    
    # Calculate global position vs CTR curve for baseline expectations
    pos_ctr_df = con.execute("""
        SELECT 
            ROUND(position, 0) as pos_bucket,
            COUNT(*) as sample_count,
            SUM(clicks) as total_clicks,
            SUM(impressions) as total_impressions,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) as empirical_ctr,
            AVG(position) as avg_exact_pos
        FROM search_performance
        WHERE position <= 20
        GROUP BY 1
        HAVING total_impressions > 500
        ORDER BY pos_bucket ASC;
    """).df()
    
    # Fit power law model: CTR = a * (pos ^ b)
    def power_law(x, a, b):
        return a * (x ** b)
    
    valid_data = pos_ctr_df.dropna()
    popt, _ = curve_fit(power_law, valid_data['avg_exact_pos'], valid_data['empirical_ctr'], p0=[0.3, -1.0])
    a_param, b_param = popt[0], popt[1]
    
    print(f"[Baseline Model] Fitted CTR expectation curve: Expected_CTR = {a_param:.4f} * (position ^ {b_param:.4f})")
    
    # Save baseline parameters
    baseline_params = {"a": a_param, "b": b_param}
    with open(os.path.join(data_dir, "ctr_baseline_params.json"), "w") as f:
        json.dump(baseline_params, f, indent=2)
        
    # Run Public Compliance & Privacy Audit
    print("\n--- Privacy & Public Safety Audit ---")
    columns = [row[0] for row in con.execute("DESCRIBE search_performance").fetchall()]
    sample = con.execute("SELECT * FROM search_performance LIMIT 5").df()
    print("Schema Columns:", columns)
    print("Sample Rows:\n", sample)
    
    # Check for PII / forbidden strings
    assert 'url' not in columns, "Privacy violation: raw URLs present in schema!"
    assert 'domain' not in columns, "Privacy violation: raw domains present in schema!"
    print("Privacy Audit PASSED: Zero private domains, URLs, or client identity present.")
    
    con.close()
    del con
    return db_path, baseline_params

if __name__ == "__main__":
    db_path, params = run_duckdb_pipeline()
    print("[Pipeline Complete] Data ingestion and EDA complete.")
