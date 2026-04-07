# GeoRisk AI

AI-powered geotechnical monitoring and risk analysis for tunnels and underground stations.

GeoRisk AI ingests sensor-like time-series data, runs feature engineering, detects anomalies, predicts failure probability, and produces a per-structure risk assessment through a FastAPI service.

## What This Project Does

- Loads datasets for training and inference (`data/train/dataset_merged.csv` and `data/external/dataset_external.csv`)
- Engineers robust, leakage-safe features (explicitly excludes target-like labels from the feature set)
- Trains:
  - An anomaly detector (IsolationForest) with scaling (StandardScaler)
  - A failure classifier (RandomForest) with a calibrated decision threshold
- Runs inference and produces:
  - Per-record probabilities/scores
  - Per-structure aggregation and ranking
  - KPIs (ROC AUC, Precision, Recall, F1, confusion matrix, anomaly detection metrics)
  - Optional narrative summary (OpenAI)

## Architecture (High Level)

```
FastAPI
  ├─ POST /train   -> training pipeline -> persists models + metadata
  └─ POST /analyze -> inference pipeline -> returns structure ranking + KPIs

Data
  ├─ train:    data/train/dataset_merged.csv
  └─ external: data/external/dataset_external.csv
```

## Project Modules

| Module | Responsibility |
|---|---|
| `app/ingestion/loader.py` | Select and load datasets (`train` vs `external`) |
| `app/features/mapping.py` | Create proxy aggregates from `feature_*` columns |
| `app/features/engineering.py` | Feature engineering + normalization; defines leakage drop list |
| `app/models/predictor.py` | Failure model train/infer; validates binary behavior and returns class-1 probability |
| `app/models/anomaly.py` | IsolationForest + StandardScaler train/infer; outputs anomaly scores |
| `app/models/risk_engine.py` | Monotonic risk composition (0–1) + categorical classification |
| `app/services/evaluation/evaluation_service.py` | KPI computation: ROC AUC, Precision, Recall, F1, confusion matrix |
| `app/services/pipeline/train_pipeline.py` | Training pipeline orchestration + metadata persistence |
| `app/services/pipeline/inference_pipeline.py` | Inference pipeline orchestration + aggregation + thresholds block |
| `app/api/routes.py` | FastAPI endpoints (`/train`, `/analyze`) |
| `app/core/config.py` | Environment-driven settings |

## Requirements

- Python 3.11 or 3.12 recommended (scikit-learn wheels may not be available for newer versions)
- Dependencies: see `requirements.txt`

## Setup

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuration

Copy environment template:

```bash
cp .env.example .env
```

Optional (narrative generation):
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default `gpt-4o-mini`)

## Model Artifacts (Where They Live)

All persisted artifacts are stored in `data/models/` by default:

- `failure_model.pkl`
- `failure_scaler.pkl`
- `anomaly_model.pkl`
- `anomaly_scaler.pkl`
- `model_metadata.json` (feature list, training metrics, and `failure_threshold`)

### Reset / Delete Saved Models

To force a clean retrain, delete everything in `data/models/`.

Windows (PowerShell):

```powershell
Remove-Item -Recurse -Force .\data\models\*
```

macOS / Linux:

```bash
rm -rf ./data/models/*
```

## Generating a New External Dataset

The external dataset generator writes:
- `data/external/dataset_external.csv`

It uses the trained feature list stored in `data/models/model_metadata.json` to keep train/inference consistent.

Steps:

1) Train once (creates `model_metadata.json`)

```bash
curl -X POST http://localhost:8000/train -H "Content-Type: application/json" -d "{}"
```

2) Generate the external dataset

```bash
python scripts/dataset_generator.py
```

## Running the API

Start the server:

```bash
uvicorn app.main:app --reload
```

Open the docs:

```
http://localhost:8000/docs
```

## API Endpoints

### `GET /health`

Simple liveness endpoint.

Example response:

```json
{ "status": "ok" }
```

### `POST /train`

Trains models using `data/train/dataset_merged.csv` and persists artifacts + metadata.

Key behaviors:
- Applies a real train/test split.
- Tunes a classification threshold on the validation split to maximize F1.
- Persists:
  - `features` list
  - `failure_threshold`
  - training metrics

Example request:

```bash
curl -X POST http://localhost:8000/train -H "Content-Type: application/json" -d "{}"
```

Example response (simplified):

```json
{
  "status": "success",
  "data": {
    "status": "models trained",
    "feature_count": 132,
    "metrics": {
      "0": { "precision": 0.95, "recall": 0.98, "f1-score": 0.96, "support": 2504 },
      "1": { "precision": 0.78, "recall": 0.56, "f1-score": 0.65, "support": 278 },
      "accuracy": 0.94,
      "roc_auc": 0.78,
      "threshold": 0.62
    }
  }
}
```

### `POST /analyze`

Runs inference using `data/external/dataset_external.csv` and returns:
- per-structure ranking (`structures[]`)
- KPI block (`kpis`)
- thresholds used in the run (`thresholds`)
- summary statistics (`summary`)
- optional narrative (`insight`)

Example request:

```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "{}"
```

Example response (simplified):

```json
{
  "structures": [
    {
      "structure_id": 3,
      "records": 1000,
      "avg_risk_score": 0.68,
      "failure_probability": 0.72,
      "risk_level": "high"
    }
  ],
  "total_structures": 1,
  "high_risk_count": 1,
  "medium_risk_count": 0,
  "low_risk_count": 0,
  "thresholds": {
    "failure": 0.62,
    "risk_high": 0.70,
    "risk_medium": 0.50,
    "anomaly_rate_target": 0.03
  },
  "kpis": {
    "failure": {
      "roc_auc": 0.75,
      "precision": 0.61,
      "recall": 0.63,
      "f1_score": 0.62,
      "confusion_matrix": [[TN, FP], [FN, TP]],
      "pred_positive_rate": 0.12
    },
    "anomaly": { "precision": 0.40, "recall": 0.35, "f1_score": 0.37 },
    "risk": { "mae": 0.18, "rmse": 0.26 }
  },
  "summary": {
    "records": 10000,
    "positive_target_count": 1084,
    "anomaly_count": 300
  }
}
```

## Risk Score

The risk score is computed per record in `app/models/risk_engine.py`:

- Scale: 0 to 1
- Monotonic by construction:
  - higher failure probability increases risk
  - higher anomaly score increases risk

Current composition:

```
risk_score = 0.5 * failure_probability
          + 0.3 * normalized_anomaly_score
          + 0.2 * strain_rate
```

## Running Tests

```bash
python -m compileall app scripts tests
```

If pytest is installed in your environment:

```bash
pytest -q
```

## Notes

- Training and analysis use different datasets by design:
  - `/train` uses `data/train/dataset_merged.csv`
  - `/analyze` uses `data/external/dataset_external.csv`
- Feature consistency is enforced through `data/models/model_metadata.json`.
