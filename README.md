# Lightweight EfficientNet-Based E-Waste Classification and Recycling Guidance System

> **5th Semester Mini-Project** | CSE | SDG 11 & SDG 12
> Team Size: 4 | Timeline: 4 weeks | Zero cost

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/ewaste-classifier.git
cd ewaste-classifier

# 2. Create a virtual environment (Python 3.10–3.12)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 4. Verify setup
python scripts/verify_setup.py

# 5. Run the backend (after Phase 6)
uvicorn backend.main:app --reload

# 6. Run the frontend (after Phase 7, in a separate terminal)
streamlit run frontend/app.py
```

---

## Folder Structure

```
ewaste-classifier/
├── classes.json                  # SINGLE SOURCE OF TRUTH for class labels
├── config.py                     # All hyperparameters and paths
├── requirements.txt              # Pinned local dependencies
├── requirements_colab.txt        # Minimal Colab-only dependencies
│
├── data/
│   ├── raw/                      # Downloaded raw images (git-ignored)
│   ├── processed/
│   │   ├── train/                # Training images by class folder
│   │   ├── val/                  # Validation images by class folder
│   │   └── test/                 # Test images by class folder
│   ├── splits/                   # train.csv, val.csv, test.csv (in git)
│   └── real_world_test/          # 20-30 phone photos for robustness testing
│
├── models/
│   ├── checkpoints/              # .pth files (git-ignored, stored on Drive)
│   └── onnx/                     # .onnx exported models (git-ignored)
│
├── notebooks/
│   └── phase2_training.ipynb     # Colab training notebook
│
├── src/
│   ├── dataset/                  # Dataset loading and preprocessing code
│   ├── model/                    # Model definitions, training loops
│   ├── guidance/                 # Knowledge base and hazard lookup
│   └── utils/
│       └── class_loader.py       # Shared label<->index converter
│
├── backend/
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Backend-specific pins (subset)
│   └── recyclers_fallback.json   # Static Bengaluru recycler list
│
├── frontend/
│   └── app.py                    # Streamlit application
│
├── tests/
│   ├── unit/                     # Unit tests (guidance, threshold logic)
│   ├── api/                      # FastAPI integration tests
│   └── robustness/               # Brightness/blur/rotation tests
│
├── docs/
│   └── report_assets/            # Figures, tables for the project report
│
├── scripts/
│   └── verify_setup.py           # One-command environment check
│
└── .github/
    └── workflows/
        └── ci.yml                # GitHub Actions: lint + unit tests
```

---

## Architecture Overview

```
[User Phone Camera / Browser Upload]
            |
            v
  +-----------------------+
  |   Streamlit Frontend  |  (Hugging Face Spaces or local)
  |   - Image upload      |
  |   - Webcam capture    |
  |   - Results card      |
  +-----------+-----------+
              | HTTP POST /predict (multipart/form-data)
              v
  +-----------------------+
  |   FastAPI Backend     |  (Render free tier or local)
  |   - File validation   |
  |   - Preprocess img    |
  |   - ONNX inference    |
  |   - Confidence check  |
  |   - Hazard lookup     |
  |   - Location lookup   |
  +-----------+-----------+
         /         \
        v           v
+------------+   +--------------------+
| ONNX Model |   | Guidance Engine    |
| (INT8 quan)|   | (knowledge_base.   |
| EfficientN |   |  json + config.py  |
| B0 ~5 MB)  |   |  threshold logic)  |
+------------+   +--------------------+
                        |
                        v
              +--------------------+
              | Location Lookup    |
              | OpenStreetMap      |
              | Nominatim API      |
              | (fallback: static  |
              |  Bengaluru JSON)   |
              +--------------------+
```

---

## Phases

| Phase | Topic | Week |
|-------|-------|------|
| 0 | Setup & Scaffold | 1 |
| 1 | Dataset Collection & Cleaning | 1 |
| 2 | Model Training (Colab) | 1–2 |
| 3 | Evaluation & Calibration | 2 |
| 4 | ONNX Export & Quantization | 2 |
| 5 | Guidance Engine (JSON KB) | 2 |
| 6 | FastAPI Backend | 3 |
| 7 | Streamlit Frontend | 3 |
| 8 | Deployment | 3 |
| 9 | Testing & Robustness | 3 |
| 10 | Documentation & Review | 4 |
| 11 | Final Integration | 4 |

---

## Team Branches (Git Workflow)

| Branch | Purpose |
|--------|---------|
| `main` | Stable, demo-ready code only. PR required. |
| `develop` | Integration branch. Merge feature branches here. |
| `feature/dataset` | Member A – Phase 1 dataset scripts |
| `feature/training` | Member B – Phase 2 training notebook |
| `feature/backend` | Member C – Phase 6 FastAPI backend |
| `feature/frontend` | Member D – Phase 7 Streamlit frontend |

**Commit message format:** `type(scope): short description`
Examples:
- `feat(dataset): add perceptual hash deduplication`
- `fix(backend): handle corrupt image upload`
- `docs(report): add confusion matrix figure`

---

## Disclaimer

This system provides **informational guidance only** and is **not** legal or
official safety advice. Always consult CPCB/KSPCB authorised recyclers and
follow India's E-Waste (Management) Rules 2022 for legal compliance.

---

## SDG Alignment

- **SDG 11** (Sustainable Cities): Nearest recycling centre lookup helps
  urban residents responsibly dispose of e-waste.
- **SDG 12** (Responsible Consumption): Hazard and handling guidance promotes
  safe, informed consumer behaviour.
