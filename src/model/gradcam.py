"""
src/model/gradcam.py
────────────────────
Grad-CAM (Gradient-weighted Class Activation Mapping) visualizer for Phase 3.
Generates heatmaps explaining model decisions on 5 diverse test images.

For each sample image:
  - Extracts target class prediction & confidence
  - Computes gradient of predicted class logit w.r.t. conv_head feature maps
  - Weights feature maps by global-average-pooled gradients
  - Overlays ReLU-activated heatmap onto original RGB image
  - Saves visualization to docs/report_assets/gradcam_sample_{i}_{label}.png
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    PROCESSED_DIR,
    CHECKPOINTS_DIR,
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    EFFICIENTNET_MODEL_NAME,
)
from src.utils.class_loader import get_class_names
from src.model.build_model import build_classifier


class GradCAM:
    """
    Hook-based Grad-CAM implementation.
    Compatible with any PyTorch convolutional backbone without external dependencies.
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register forward & backward hooks
        self.target_layer.register_forward_hook(self._forward_hook)
        self.target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: int | None = None) -> np.ndarray:
        self.model.eval()
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = int(torch.argmax(output, dim=1).item())

        self.model.zero_grad()
        loss = output[0, class_idx]
        loss.backward()

        # Global average pooling of gradients: weights alpha_k
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        # Weighted combination of activation maps
        cam = torch.sum(weights * self.activations, dim=1).squeeze()
        # ReLU to keep only features that have a positive influence
        cam = torch.clamp(cam, min=0)
        
        cam_np = cam.cpu().numpy()
        # Normalize to [0, 1]
        if np.max(cam_np) > 0:
            cam_np = cam_np / np.max(cam_np)
        return cam_np


def overlay_cam_on_image(img_pil: Image.Image, cam: np.ndarray, alpha: float = 0.5) -> Image.Image:
    """Overlays resized colormap heatmap onto original PIL image."""
    cam_resized = Image.fromarray((cam * 255).astype(np.uint8)).resize(
        img_pil.size, resample=Image.Resampling.BILINEAR
    )
    cam_arr = np.array(cam_resized) / 255.0
    
    # Apply colormap (jet / magma)
    cmap = plt.get_cmap("jet")
    heatmap = cmap(cam_arr)[:, :, :3]  # drop alpha
    heatmap = (heatmap * 255).astype(np.uint8)
    
    img_arr = np.array(img_pil.convert("RGB"))
    blended = (alpha * heatmap + (1 - alpha) * img_arr).astype(np.uint8)
    return Image.fromarray(blended)


def run_gradcam(model_name: str = EFFICIENTNET_MODEL_NAME):
    class_names = get_class_names()
    num_classes = len(class_names)
    device = torch.device("cpu")

    ckpt_path = CHECKPOINTS_DIR / f"{model_name}_best.pth"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}")

    model = build_classifier(model_name=model_name, num_classes=num_classes, pretrained=False)
    ckpt = torch.load(ckpt_path, map_location=device)
    state = ckpt["model_state"] if "model_state" in ckpt else ckpt
    model.load_state_dict(state)
    model.eval()

    # Identify target conv layer
    if hasattr(model, "conv_head"):
        target_layer = model.conv_head
    elif hasattr(model, "blocks"):
        target_layer = model.blocks[-1]
    else:
        # Fallback to last Conv2d layer
        conv_layers = [m for m in model.modules() if isinstance(m, nn.Conv2d)]
        target_layer = conv_layers[-1]

    cam_engine = GradCAM(model, target_layer)

    preprocess = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    test_dir = PROCESSED_DIR / "test"
    report_dir = PROJECT_ROOT / "docs" / "report_assets"
    report_dir.mkdir(parents=True, exist_ok=True)

    # Pick 5 distinct test classes to visualize
    sample_classes = ["battery", "cfl_bulb", "keyboard", "mobile_phone", "pcb"]
    visualized = 0

    print(f"\n{'='*65}")
    print(f"  Generating Grad-CAM Visualizations ({model_name})")
    print(f"{'='*65}\n")

    fig, axes = plt.subplots(len(sample_classes), 2, figsize=(8, 3.2 * len(sample_classes)))

    for i, cls in enumerate(sample_classes):
        cls_dir = test_dir / cls
        if not cls_dir.exists():
            continue
        imgs = sorted(list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png")))
        if not imgs:
            continue
        
        sample_path = imgs[0]
        raw_img = Image.open(sample_path).convert("RGB")
        tensor = preprocess(raw_img).unsqueeze(0).to(device)

        # Predict
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=-1)
            pred_idx = int(torch.argmax(probs, dim=-1).item())
            confidence = float(probs[0, pred_idx].item())

        # Heatmap
        cam = cam_engine.generate_heatmap(tensor, class_idx=pred_idx)
        overlay = overlay_cam_on_image(raw_img.resize((IMAGE_SIZE, IMAGE_SIZE)), cam)

        # Plot
        axes[i, 0].imshow(raw_img.resize((IMAGE_SIZE, IMAGE_SIZE)))
        axes[i, 0].set_title(f"Sample {i+1}: True = {cls}")
        axes[i, 0].axis("off")

        pred_name = class_names[pred_idx]
        correct_flag = "OK" if pred_name == cls else "MISCLASSIFIED"
        axes[i, 1].imshow(overlay)
        axes[i, 1].set_title(f"Grad-CAM [{correct_flag}]\nPred: {pred_name} ({confidence*100:.1f}%)")
        axes[i, 1].axis("off")

        # Also save individual high-res image
        indiv_path = report_dir / f"gradcam_sample_{i+1}_{cls}.png"
        overlay.save(indiv_path)
        print(f"  Sample {i+1} ({cls}): Predicted {pred_name} ({confidence*100:.1f}%) -> {indiv_path}")
        visualized += 1

    plt.tight_layout()
    grid_path = report_dir / "gradcam_grid.png"
    plt.savefig(grid_path, dpi=150)
    plt.close()
    print(f"\n  Combined Grad-CAM grid saved: {grid_path}\n")


if __name__ == "__main__":
    run_gradcam()
