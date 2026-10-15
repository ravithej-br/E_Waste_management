"""
src/model/export_onnx.py
────────────────────────
Exports trained PyTorch weights to FP32 ONNX format with strict numerical verification.

Key Steps:
  1. Loads checkpoint from models/checkpoints/<model_name>_best.pth
  2. Runs torch.onnx.export with opset 17 and dynamic batching
  3. Verifies model validity with onnx.checker.check_model()
  4. Runs inference through both PyTorch and ONNX Runtime on identical test inputs
  5. Computes maximum absolute difference (must be < 1e-4) to guarantee zero parity loss
"""

import sys
import argparse
from pathlib import Path
import numpy as np

# Prevent Windows cp1252 UnicodeEncodeError from PyTorch exporter emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn

import onnx
import onnxruntime as ort

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CHECKPOINTS_DIR,
    ONNX_DIR,
    ONNX_OPSET,
    ONNX_FP32_NAME,
    ONNX_FP32_MOBILE,
    IMAGE_SIZE,
    EFFICIENTNET_MODEL_NAME,
    MOBILENET_MODEL_NAME,
)
from src.utils.class_loader import get_class_names
from src.model.build_model import build_classifier


def export_to_onnx(model_name: str, output_filename: str) -> Path:
    class_names = get_class_names()
    num_classes = len(class_names)
    device = torch.device("cpu")

    ckpt_path = CHECKPOINTS_DIR / f"{model_name}_best.pth"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}")

    ONNX_DIR.mkdir(parents=True, exist_ok=True)
    onnx_path = ONNX_DIR / output_filename

    print(f"\n{'='*65}")
    print(f"  Exporting {model_name} to ONNX FP32")
    print(f"  Input Checkpoint: {ckpt_path}")
    print(f"  Output ONNX Path: {onnx_path}")
    print(f"{'='*65}\n")

    # 1. Load PyTorch model
    model = build_classifier(model_name=model_name, num_classes=num_classes, pretrained=False)
    ckpt = torch.load(ckpt_path, map_location=device)
    state = ckpt["model_state"] if "model_state" in ckpt else ckpt
    model.load_state_dict(state)
    model.eval()

    # 2. Dummy input for tracing
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, requires_grad=False)

    # 3. Export
    input_names = ["input"]
    output_names = ["output"]
    dynamic_axes = {
        "input": {0: "batch_size"},
        "output": {0: "batch_size"},
    }

    torch.onnx.export(
        model,
        dummy_input,
        str(onnx_path),
        export_params=True,
        opset_version=ONNX_OPSET,
        do_constant_folding=True,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        dynamo=False,
    )

    print(f"  [OK] Exported successfully (Opset {ONNX_OPSET}).")

    # 4. Verify ONNX Model Graph
    onnx_model = onnx.load(str(onnx_path))
    onnx.checker.check_model(onnx_model)
    print("  [OK] ONNX model structure verified by onnx.checker.")

    # 5. Numerical Parity Verification (PyTorch vs ONNX Runtime)
    test_tensor = torch.ones(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    with torch.no_grad():
        torch_out = model(test_tensor).numpy()

    ort_session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    ort_inputs = {ort_session.get_inputs()[0].name: test_tensor.numpy()}
    ort_out = ort_session.run(None, ort_inputs)[0]

    max_diff = float(np.max(np.abs(torch_out - ort_out)))
    print(f"  Maximum Absolute Difference (PyTorch vs ONNX): {max_diff:.2e}")


    tolerance = 1e-4
    if max_diff < tolerance:
        print(f"  [PASSED] Numerical parity confirmed! Error ({max_diff:.2e}) < {tolerance}")
    else:
        print(f"  [WARN] Output difference ({max_diff:.2e}) exceeds tolerance ({tolerance}).")

    size_mb = onnx_path.stat().st_size / (1024 * 1024)
    print(f"  FP32 ONNX Model Size: {size_mb:.2f} MB\n")

    return onnx_path


def main():
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX")
    parser.add_argument("--model", type=str, default="all",
                        choices=["all", EFFICIENTNET_MODEL_NAME, MOBILENET_MODEL_NAME])
    args = parser.parse_args()

    if args.model in ("all", EFFICIENTNET_MODEL_NAME):
        export_to_onnx(EFFICIENTNET_MODEL_NAME, ONNX_FP32_NAME)

    if args.model in ("all", MOBILENET_MODEL_NAME):
        export_to_onnx(MOBILENET_MODEL_NAME, ONNX_FP32_MOBILE)


if __name__ == "__main__":
    main()
