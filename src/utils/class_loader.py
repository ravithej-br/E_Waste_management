"""
src/utils/class_loader.py
─────────────────────────
Utility that loads classes.json and provides label↔index conversions.
Imported by training, evaluation, ONNX export, backend, and frontend.
This guarantees the class order can never mismatch between phases.
"""

import json
from pathlib import Path
from typing import Dict, List


def load_classes(classes_json_path: str | Path | None = None) -> Dict:
    """
    Load classes.json and return the full dict.

    Parameters
    ----------
    classes_json_path : str or Path, optional
        Path to classes.json. Defaults to PROJECT_ROOT/classes.json
        by walking up from this file's location.

    Returns
    -------
    dict with keys: classes, num_classes, unknown_class, unknown_index
    """
    if classes_json_path is None:
        # Walk up to project root (two levels above src/utils/)
        classes_json_path = Path(__file__).resolve().parent.parent.parent / "classes.json"

    classes_json_path = Path(classes_json_path)
    if not classes_json_path.exists():
        raise FileNotFoundError(f"classes.json not found at {classes_json_path}")

    with open(classes_json_path, "r") as f:
        data = json.load(f)

    required_keys = {"classes", "num_classes", "unknown_class", "unknown_index"}
    if not required_keys.issubset(data.keys()):
        raise ValueError(f"classes.json is missing keys: {required_keys - data.keys()}")

    return data


def get_class_names(classes_json_path: str | Path | None = None) -> List[str]:
    """Return ordered list of class name strings."""
    return load_classes(classes_json_path)["classes"]


def get_label_to_index(classes_json_path: str | Path | None = None) -> Dict[str, int]:
    """Return mapping of class name → integer index."""
    return {name: idx for idx, name in enumerate(get_class_names(classes_json_path))}


def get_index_to_label(classes_json_path: str | Path | None = None) -> Dict[int, str]:
    """Return mapping of integer index → class name."""
    return {idx: name for idx, name in enumerate(get_class_names(classes_json_path))}


# ── Quick sanity check ──────────────────────────────────────────────────────
if __name__ == "__main__":
    names = get_class_names()
    print(f"Loaded {len(names)} classes: {names}")
    print("label→index:", get_label_to_index())
    print("index→label:", get_index_to_label())
