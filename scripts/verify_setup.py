"""
scripts/verify_setup.py
-----------------------
Run this after installing requirements.txt to confirm every dependency
loads correctly and classes.json is valid.

Usage (Windows PowerShell):
    python scripts/verify_setup.py

Usage (Linux / macOS / Colab):
    python scripts/verify_setup.py
"""

import sys
import json
from pathlib import Path

REQUIRED_PYTHON = (3, 10)   # minimum; 3.10, 3.11, 3.12 all accepted


def check(label: str, fn):
    try:
        result = fn()
        suffix = f"  [{result}]" if result else ""
        print(f"  [OK]   {label}{suffix}")
    except Exception as e:
        print(f"  [FAIL] {label}  ERROR: {e}")
        return False
    return True


def main():
    print("")
    print("=" * 57)
    print("   E-Waste Classifier - Setup Verification")
    print("=" * 57)
    print("")

    # Python version
    pv = sys.version_info
    ok = pv >= REQUIRED_PYTHON
    tag = "[OK]  " if ok else "[FAIL]"
    print(f"  {tag} Python {pv.major}.{pv.minor}.{pv.micro}"
          f"  (need >= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]})")

    print("\n-- Core ML -------------------------------------------")
    check("torch",       lambda: __import__("torch").__version__)
    check("torchvision", lambda: __import__("torchvision").__version__)
    check("timm",        lambda: __import__("timm").__version__)

    print("\n-- ONNX ----------------------------------------------")
    check("onnx",        lambda: __import__("onnx").__version__)
    check("onnxruntime", lambda: __import__("onnxruntime").__version__)

    print("\n-- Data science --------------------------------------")
    check("numpy",       lambda: __import__("numpy").__version__)
    check("pandas",      lambda: __import__("pandas").__version__)
    check("sklearn",     lambda: __import__("sklearn").__version__)
    check("matplotlib",  lambda: __import__("matplotlib").__version__)
    check("seaborn",     lambda: __import__("seaborn").__version__)

    print("\n-- Image utilities -----------------------------------")
    check("PIL (Pillow)", lambda: __import__("PIL").__version__)
    check("imagehash",   lambda: __import__("imagehash").__version__)
    check("cv2 (opencv)", lambda: __import__("cv2").__version__)

    print("\n-- Backend / Frontend --------------------------------")
    check("fastapi",     lambda: __import__("fastapi").__version__)
    check("uvicorn",     lambda: __import__("uvicorn").__version__)
    check("streamlit",   lambda: __import__("streamlit").__version__)
    check("httpx",       lambda: __import__("httpx").__version__)
    check("slowapi",     lambda: __import__("slowapi").__version__)

    print("\n-- Testing -------------------------------------------")
    check("pytest",      lambda: __import__("pytest").__version__)

    print("\n-- Grad-CAM ------------------------------------------")
    check("pytorch_grad_cam", lambda: __import__("pytorch_grad_cam") and "ok")

    print("\n-- Project files -------------------------------------")
    root = Path(__file__).resolve().parent.parent

    # classes.json
    cj = root / "classes.json"
    if cj.exists():
        with open(cj) as f:
            data = json.load(f)
        print(f"  [OK]   classes.json  [{data['num_classes']} classes: {data['classes']}]")
    else:
        print(f"  [FAIL] classes.json  NOT FOUND at {cj}")

    # config.py
    cfg = root / "config.py"
    tag2 = "[OK]  " if cfg.exists() else "[FAIL]"
    print(f"  {tag2} config.py  {'found' if cfg.exists() else 'MISSING'}")

    print("\n-- GPU -----------------------------------------------")
    import torch
    if torch.cuda.is_available():
        print(f"  [OK]   CUDA GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("  [WARN] No CUDA GPU found - training will be slow on CPU.")
        print("         Use Google Colab: Runtime -> Change runtime -> T4 GPU.")

    print("")
    print("=" * 57)
    print("")


if __name__ == "__main__":
    main()
