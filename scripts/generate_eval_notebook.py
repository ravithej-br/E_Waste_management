"""
scripts/generate_eval_notebook.py
─────────────────────────────────
Generates notebooks/phase3_evaluation.ipynb for Phase 3 evaluation & Grad-CAM analysis.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "phase3_evaluation.ipynb"

def make_cell(cell_type: str, source: list[str]) -> dict:
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": [s + "\n" for s in source]
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

cells = []

cells.append(make_cell("markdown", [
    "# Phase 3: Comprehensive Model Evaluation, Grad-CAM & Confidence Calibration",
    "### Project: Lightweight EfficientNet-B0 E-Waste Classifier",
    "This notebook evaluates the trained models on the **695 independent test samples**, produces confusion matrices, runs Grad-CAM explainability, and performs Temperature Scaling calibration.",
]))

cells.append(make_cell("code", [
    "# Run full test evaluation and latency benchmark",
    "!python src/model/evaluate.py --model all",
]))

cells.append(make_cell("code", [
    "# Run Confidence Calibration & Temperature Scaling",
    "!python src/model/calibrate.py",
]))

cells.append(make_cell("code", [
    "# Generate Grad-CAM feature attribution maps",
    "!python src/model/gradcam.py",
]))

cells.append(make_cell("code", [
    "# Display evaluation assets",
    "from IPython.display import Image, display",
    "print('Confusion Matrix (EfficientNet-B0):')",
    "display(Image('docs/report_assets/confusion_matrix_efficientnet_b0.png'))",
    "print('Reliability Diagram (Temperature Scaling):')",
    "display(Image('docs/report_assets/reliability_diagram.png'))",
    "print('Grad-CAM Visual Explanations:')",
    "display(Image('docs/report_assets/gradcam_grid.png'))",
]))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print(f"[SUCCESS] Generated {NOTEBOOK_PATH}")
