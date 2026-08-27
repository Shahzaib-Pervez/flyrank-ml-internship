# Search Intelligence Capstone: Content Refresh Opportunity Scoring Model

This repository contains the complete, end-to-end Machine Learning Capstone for **Search Intelligence (Lane 2: Refresh / Content Opportunity Scoring)** built on the **FlyRank ML Internship dataset**.

## 🚀 Deployed Research Paper

The capstone is published as a deployed, interactive web research paper:
- **Public Research Paper URL**: Listed in `submission/paper_url.txt` (`https://shahzaibpervez54.github.io/flyrank-search-intelligence-capstone/`)
- **Live Local Paper**: Open `index.html` in any web browser.

---

## 📂 Repository Structure

```
├── work/
│   ├── 01_eda_and_data_pipeline.py & .ipynb
│   ├── 02_feature_engineering.py & .ipynb
│   ├── 03_model_training_and_evaluation.py & .ipynb
│   ├── 04_capstone_refresh_opportunity_scoring.py & .ipynb
│   └── capstone_refresh_opportunity_scoring.ipynb  (Master Notebook)
├── submission/
│   └── paper_url.txt                                 (Mandatory Submission URL File)
├── data/
│   ├── search_intelligence.duckdb
│   ├── feature_matrix.parquet
│   ├── ctr_baseline_params.json
│   ├── evaluation_metrics.json
│   ├── feature_importances.json
│   └── ranked_recommendations.json
├── index.html                                        (Web Research Paper UI)
├── styles.css                                         (Design System & Typography)
├── script.js                                          (Interactive Charts & Filter Engine)
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart & Reproducibility

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Pipeline
```bash
python work/01_eda_and_data_pipeline.py
python work/02_feature_engineering.py
python work/03_model_training_and_evaluation.py
python work/04_capstone_opportunity_scoring.py
```

---

## 📊 Summary of Model Performance

| Model | ROC-AUC | PR-AUC | F1-Score | Precision | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hist Gradient Boosting (Champion)** | **0.9999** | **0.9999** | **0.9980** | **0.9961** | **1.0000** |
| Random Forest Classifier | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Logistic Regression | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Rule-Based Baseline | 0.9398 | 0.9691 | 1.0000 | 1.0000 | 1.0000 |

---

## 🔒 Public Safety & Privacy Compliance

This project strictly follows public submission rules:
- Zero raw URLs, private domains, or credentials.
- Anonymized feature vectors (`page_1000`, `query_cluster_X`).
- No causal algorithm claims regarding Google's ranking algorithms.

---

## 🏷️ Credit & Acknowledgments

Built on the [FlyRank ML Internship dataset](https://flyrank.ai).
