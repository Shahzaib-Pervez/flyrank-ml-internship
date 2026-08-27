"""
===============================================================================
CREATE_NOTEBOOKS.PY
Generates structured, well-commented Jupyter Notebooks (.ipynb) for submission.
===============================================================================
"""
import os
import json

def py_to_notebook(title, description, py_code_content, output_path):
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {title}\n",
                    f"**FlyRank Search Intelligence Capstone Project**\n\n",
                    f"{description}\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": py_code_content.splitlines(keepends=True)
            }
        ],
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"[Notebook Created] {output_path}")

def build_all_notebooks():
    work_dir = "work"
    os.makedirs(work_dir, exist_ok=True)
    
    with open(os.path.join(work_dir, "01_eda_and_data_pipeline.py"), "r", encoding="utf-8") as f:
        code_01 = f.read()
    py_to_notebook(
        "01 Data Aggregation & EDA Pipeline over FlyRank Search Warehouse",
        "Initializes DuckDB connection, aggregates daily search log metrics across 90-day window, fits baseline CTR power-law curve, and executes public privacy compliance audit.",
        code_01,
        os.path.join(work_dir, "01_eda_and_data_pipeline.ipynb")
    )
    
    with open(os.path.join(work_dir, "02_feature_engineering.py"), "r", encoding="utf-8") as f:
        code_02 = f.read()
    py_to_notebook(
        "02 Search Intelligence Feature Engineering & Opportunity Labels",
        "Engineers rolling window metrics: 30d vs 90d position drift, empirical CTR deficit ratios, click decay velocity, and binary target labels.",
        code_02,
        os.path.join(work_dir, "02_feature_engineering.ipynb")
    )

    with open(os.path.join(work_dir, "03_model_training_and_evaluation.py"), "r", encoding="utf-8") as f:
        code_03 = f.read()
    py_to_notebook(
        "03 Cross-Validation, Baseline Benchmarking & Model Evaluation",
        "Evaluates HistGradientBoosting, RandomForest, and LogisticRegression against Rule-Based Baseline using 5-fold Stratified K-Fold. Computes ROC-AUC, PR-AUC, confusion matrices, and feature importances.",
        code_03,
        os.path.join(work_dir, "03_model_training_and_evaluation.ipynb")
    )

    with open(os.path.join(work_dir, "04_capstone_opportunity_scoring.py"), "r", encoding="utf-8") as f:
        code_04 = f.read()
    py_to_notebook(
        "04 Continuous Opportunity Scoring Engine & Action Playbook",
        "Applies champion model to assign 0-100 opportunity scores, diagnostic reason codes (DECAY_POSITION_SLIP, CTR_UNDERPERFORMING), and ranked content refresh playbooks.",
        code_04,
        os.path.join(work_dir, "04_capstone_refresh_opportunity_scoring.ipynb")
    )

    # Combine all code for master capstone_refresh_opportunity_scoring.ipynb
    master_code = code_01 + "\n\n# ==========================================\n# STEP 2: FEATURE ENGINEERING\n# ==========================================\n" + code_02 + "\n\n# ==========================================\n# STEP 3: MODELING & CV EVALUATION\n# ==========================================\n" + code_03 + "\n\n# ==========================================\n# STEP 4: OPPORTUNITY SCORING ENGINE\n# ==========================================\n" + code_04
    py_to_notebook(
        "FlyRank Search Intelligence Capstone: Master Pipeline Notebook",
        "Complete end-to-end executable capstone notebook: DuckDB ingestion, feature engineering, leak-free CV modeling, evaluation, and ranked content opportunity scoring engine.",
        master_code,
        os.path.join(work_dir, "capstone_refresh_opportunity_scoring.ipynb")
    )

if __name__ == "__main__":
    build_all_notebooks()
