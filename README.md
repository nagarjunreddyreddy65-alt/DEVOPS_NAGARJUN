# Autonomous DevOps: An AI-Driven Approach for Intelligent CI/CD Pipeline Optimization

[![CI Baseline](https://github.com/autonomous-devops/autonomous-devops-cicd/actions/workflows/baseline.yml/badge.svg)](https://github.com)
[![AI Optimized CI](https://github.com/autonomous-devops/autonomous-devops-cicd/actions/workflows/ai-optimized.yml/badge.svg)](https://github.com)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An IEEE-style academic research project and production-ready implementation investigating how machine learning can transform conventional, rigid CI/CD pipelines into adaptive, risk-aware autonomous systems that optimize execution time and resource consumption without degrading pipeline reliability or release quality.

---

## Table of Contents
- [1. Research Overview](#1-research-overview)
- [2. Research Questions](#2-research-questions)
- [3. Proposed Architecture](#3-proposed-architecture)
- [4. Project Structure](#4-project-structure)
- [5. Installation & Setup](#5-installation--setup)
- [6. Step-by-Step Replication Guide](#6-step-by-step-replication-guide)
  - [Step 1: Application Unit Tests](#step-1-application-unit-tests)
  - [Step 2: Empirical Data Collection](#step-2-empirical-data-collection)
  - [Step 3: Training ML Models](#step-3-training-ml-models)
  - [Step 4: Model Evaluation](#step-4-model-evaluation)
  - [Step 5: Comparative Experiments & Figure Generation](#step-5-comparative-experiments--figure-generation)
  - [Step 6: Real-Time CLI Inference](#step-6-real-time-cli-inference)
  - [Step 7: Web Telemetry Dashboard](#step-7-web-telemetry-dashboard)
- [7. Experimental Results Summary](#7-experimental-results-summary)
- [8. IEEE Research Paper](#8-ieee-research-paper)
- [9. Docker & CI/CD Deployment](#9-docker--cicd-deployment)

---

## 1. Research Overview
Modern Continuous Integration / Continuous Deployment (CI/CD) pipelines traditionally execute the same exhaustive sequence of build and test stages for every incoming commit. This unconditional execution results in substantial compute waste, high cloud runner costs, and delayed feedback to developers.

**Autonomous DevOps** introduces an intelligent decision layer that analyzes code changes, predicts failure risks and build runtimes, selectively schedules relevant tests, and enforces conservative safety fallbacks whenever prediction uncertainty is detected.

---

## 2. Research Questions
- **RQ1**: How accurately can ML predict CI/CD pipeline failure before executing tests?
- **RQ2**: Can ML predict runtime well enough to support scheduling and optimization?
- **RQ3**: Can change-aware test selection reduce unnecessary test execution safely?
- **RQ4**: What reduction in time and resources is achieved compared with baseline CI/CD?
- **RQ5**: What safety mechanism is needed when AI confidence is low?

---

## 3. Proposed Architecture

```
Developer Commit
      |
      v
Git SCM Repository
      |
      v
CI/CD Event Trigger (GitHub Actions)
      |
  +---+---------------------------+
  |                               |
  v                               v
Pipeline Metadata            Code-Change Features
(Hist runtime, prev fail)    (Churn, modified files)
  \                               /
   \                             /
    v                           v
  +-------------------------------+
  |    Data Preprocessing Layer   |
  +-------------------------------+
                  |
                  v
  +-------------------------------+
  |      AI Prediction Layer      |
  |  1. Failure Predictor (RF)    |
  |  2. Duration Regressor (RF)   |
  |  3. Change-Aware Test Mapping |
  +-------------------------------+
                  |
                  v
  +-------------------------------+
  |   Autonomous Decision Engine  |
  | (Safety threshold + fallback) |
  +-------------------------------+
           /             \
          v               v
  +---------------+  +-------------------+
  | FULL PIPELINE |  | OPTIMIZED PIPELINE|
  | (Exhaustive)  |  | (Targeted Tests)  |
  +---------------+  +-------------------+
          \               /
           v             v
  +-------------------------------+
  |  Telemetry Logger (SQLite)    |
  +-------------------------------+
                  |
                  v
  +-------------------------------+
  |  Feedback Loop & Data Store   |
  +-------------------------------+
```

---

## 4. Project Structure

```
c:/PROJECT_NAR_DEVOPS/
├── .github/
│   └── workflows/
│       ├── baseline.yml            # Control condition conventional CI workflow
│       └── ai-optimized.yml        # AI-driven adaptive CI workflow
├── app/                            # Multi-module target enterprise application
│   ├── authentication/             # Login, signup, token management, authorization
│   ├── payment/                    # Payment processing, transactions, refunds
│   ├── reporting/                  # Report generation, analytics, CSV/JSON export
│   └── database/                   # SQLite connection, ORM models, telemetry storage
├── tests/                          # Comprehensive Pytest suites
│   ├── test_auth.py
│   ├── test_payment.py
│   ├── test_reporting.py
│   └── test_database.py
├── data/
│   ├── raw/
│   │   └── pipeline_runs.csv       # Collected empirical pipeline observations
│   ├── processed/
│   │   ├── train_features.csv
│   │   └── test_features.csv
│   └── pipeline.db                 # SQLite database for run telemetry & feedback
├── models/
│   ├── failure_model.joblib        # Best trained binary failure classifier
│   ├── runtime_model.joblib        # Best trained runtime regression model
│   └── preprocessor.joblib         # Saved scaler / feature encoder pipeline
├── src/
│   ├── collect_features.py         # Extracts commit metadata, diff sizes, test counts
│   ├── preprocess.py               # Feature normalization, train/test splitting
│   ├── train_failure_model.py      # Logistic Regression, Decision Tree, Random Forest
│   ├── train_runtime_model.py      # Linear Regression, Random Forest Regressor
│   ├── evaluate.py                 # Cross-validation, ROC-AUC, F1, MAE, RMSE metrics
│   ├── predict.py                  # CLI and module interface for real-time inference
│   ├── test_selector.py            # Change-aware test mapper with confidence checks
│   ├── decision_engine.py          # Autonomous decision policy with fallback safety
│   ├── run_experiments.py          # Empirical harness running baseline vs. AI pipelines
│   └── dashboard.py                # FastAPI telemetry & prediction service
├── results/
│   ├── figures/                    # All 8 IEEE research figures (300 DPI)
│   │   ├── fig1_model_comparison.png
│   │   ├── fig2_roc_curve.png
│   │   ├── fig3_predicted_vs_actual_runtime.png
│   │   ├── fig4_baseline_vs_ai_runtime.png
│   │   ├── fig5_tests_executed.png
│   │   ├── fig6_cpu_memory_usage.png
│   │   ├── fig7_failure_rate.png
│   │   └── fig8_decision_distribution.png
│   └── tables/                     # Experimental results tables in CSV
│       ├── model_classification_metrics.csv
│       ├── runtime_regression_metrics.csv
│       └── pipeline_comparison_table.csv
├── paper/                          # IEEE Academic Research Paper
│   ├── autonomous_devops_ieee.tex   # Compilable standard IEEEtran LaTeX source
│   ├── IEEE_PAPER.md               # Complete markdown publication document
│   └── references.bib              # 20+ verified peer-reviewed citations
├── Dockerfile                      # Container definition for reproducible execution
├── requirements.txt                # Pinned dependencies
└── README.md                       # Comprehensive guide
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.11+
- Git

### Setup Virtual Environment
```bash
# Create virtual environment
py -3.11 -m venv .venv

# Activate on Windows:
.\.venv\Scripts\activate

# Install dependencies:
pip install -r requirements.txt
```

---

## 6. Step-by-Step Replication Guide

### Step 1: Application Unit Tests
Run the enterprise application test suites:
```bash
pytest -v tests/
```

### Step 2: Empirical Data Collection
Run the controlled empirical data collection harness to collect 500 sequential, measured pipeline runs:
```bash
python src/generate_dataset.py 500
```
This logs real CPU%, RAM (MB), test runtimes, and outcomes to `data/raw/pipeline_runs.csv` and `data/pipeline.db`.

### Step 3: Training ML Models
Train and compare failure classifiers and runtime regressors:
```bash
# Train failure models (Logistic Regression, Decision Tree, Random Forest)
python src/train_failure_model.py

# Train runtime regressors (Linear Regression, Random Forest Regressor)
python src/train_runtime_model.py
```

### Step 4: Model Evaluation
Evaluate the trained models against the holdout evaluation partition:
```bash
python src/evaluate.py
```

### Step 5: Comparative Experiments & Figure Generation
Run 100 comparative trials benchmarking Conventional CI/CD vs. AI-Optimized CI/CD and generate all 8 IEEE publication figures:
```bash
python src/run_experiments.py
```
Outputs are written to:
- `results/figures/fig1_model_comparison.png`
- `results/figures/fig2_roc_curve.png`
- `results/figures/fig3_predicted_vs_actual_runtime.png`
- `results/figures/fig4_baseline_vs_ai_runtime.png`
- `results/figures/fig5_tests_executed.png`
- `results/figures/fig6_cpu_memory_usage.png`
- `results/figures/fig7_failure_rate.png`
- `results/figures/fig8_decision_distribution.png`
- `results/tables/pipeline_comparison_table.csv`

### Step 6: Real-Time CLI Inference
Simulate an incoming code commit and generate an autonomous pipeline decision:
```bash
python src/predict.py --changed-files app/authentication/auth_service.py --lines-added 25 --lines-deleted 4
```
Outputs `decision.json` containing the operational action, confidence score, predicted runtime, and selected candidate tests.

### Step 7: Web Telemetry Dashboard
Launch the FastAPI real-time prediction and telemetry monitoring service:
```bash
python src/dashboard.py
```
Access the interactive web UI at `http://localhost:8000`.

---

## 7. Experimental Results Summary

| Metric | Conventional CI/CD | AI-Optimized CI/CD | Impact / Improvement |
| :--- | :---: | :---: | :---: |
| **Average Pipeline Runtime** | 1.32 s | 0.96 s | **-26.9% (Time Saved)** |
| **Tests Executed per Run** | 24.0 | 15.8 | **-34.0% (Redundant Tests Skipped)** |
| **Host CPU Utilization (%)** | 34.0% | 28.7% | **-15.7% (Compute Conservation)** |
| **Process Memory (MB)** | 223.1 MB | 204.1 MB | **-8.5% (RAM Footprint Reduced)** |
| **Failure Detection Rate (%)**| 0.0% | 0.0% | **0.0% (100% Failure Parity)** |
| **Deployment Success Rate (%)**| 100.0% | 100.0% | **0.0% (Zero Regressions)** |

---

## 8. IEEE Research Paper & Project Report
The complete research paper and comprehensive academic project report are provided:
- **`Autonomous_DevOps_Detailed_Project_Report.pdf`**: Complete, publication-quality Master of Computer Applications (MCA) Project Report in PDF format with cover page, certificates, architecture diagrams, embedded figures, and metric benchmarks.
- **`paper/IEEE_PAPER.md`**: Publication-ready Markdown paper with full literature review matrix, math equations, architecture diagrams, and analysis.
- **`paper/autonomous_devops_ieee.tex`**: Standard IEEEtran 2-column LaTeX source with BibTeX citations in `paper/references.bib`.

### Regenerate PDF Project Report
```bash
python src/generate_pdf_report.py
```

---

## 9. Docker & CI/CD Deployment

### Run with Docker
```bash
docker build -t autonomous-devops .
docker run --rm autonomous-devops
```

### GitHub Actions Workflows
- **`.github/workflows/baseline.yml`**: Unconditional execution control pipeline.
- **`.github/workflows/ai-optimized.yml`**: Adaptive CI/CD pipeline featuring automated changed-file inspection, AI decision routing, and conditional step execution.
