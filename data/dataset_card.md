# Dataset Card — E-Waste Classifier
# Version: 1.0  |  Last Updated: FILL_IN  |  Authors: FILL_IN

---

## Summary

A multi-source image dataset for classifying 7 categories of electronic waste
and non-e-waste items, assembled for an academic mini-project aligned with
SDG 11 and SDG 12.

---

## Classes

| Index | Class        | Description                              |
|-------|--------------|------------------------------------------|
| 0     | battery      | Alkaline, lithium, NiMH batteries        |
| 1     | cfl_bulb     | Compact fluorescent lamps                |
| 2     | keyboard     | USB and wireless keyboards               |
| 3     | mobile_phone | Smartphones and feature phones           |
| 4     | monitor_crt  | Cathode ray tube monitors                |
| 5     | pcb          | Printed circuit boards                   |
| 6     | other        | Non-e-waste / ambiguous items            |

---

## Sources

| ID  | Dataset Name                   | Platform      | Licence    | Used Classes         | Status  |
|-----|--------------------------------|---------------|------------|----------------------|---------|
| DS1 | akshat103/e-waste-image-dataset| Kaggle        | Open (VERIFY)| battery, keyboard, mobile, monitor_crt, other | Confirmed |
| DS2 | 4w4kt/waste-dataset-image      | Hugging Face  | CC BY-NC-SA 4.0 (VERIFY)| cfl_bulb ('light bulbs') | Confirmed |
| DS4 | aryaminus/electronic-components| Kaggle        | Open (VERIFY)| pcb (IC chips, microchips, microprocessors, memory-chips) | Confirmed |

---

## Image Counts (Real Data Post-Cleaning)

| Class        | Train | Val | Test | Total Clean |
|--------------|-------|-----|------|-------------|
| battery      | 206   | 45  | 44   | 295         |
| cfl_bulb     | 141   | 30  | 30   | 201         |
| keyboard     | 207   | 44  | 45   | 296         |
| mobile_phone | 204   | 43  | 44   | 291         |
| monitor_crt  | 200   | 43  | 42   | 285         |
| pcb          | 1282  | 275 | 275  | 1832        |
| other        | 1003  | 215 | 215  | 1433        |
| **TOTAL**    | **3243** | **695** | **695** | **4633** |

Split ratio: 70% / 15% / 15%  |  Seed: 42


---

## Preprocessing Steps

1. Ingested raw images and applied class mapping (`src/dataset/ingest.py`).
2. Removed corrupt images (PIL verify + load).
3. Removed near-duplicates with perceptual hashing (pHash, threshold=8)
   **before** splitting — prevents data leakage.
4. Stratified 70/15/15 split with fixed seed 42 (`src/dataset/split.py`).
5. Copied into PyTorch ImageFolder structure (`src/dataset/organise_folders.py`).

---

## Known Biases and Limitations

| Bias                  | Description                                         | Mitigation |
|-----------------------|-----------------------------------------------------|------------|
| Background bias       | Some classes (e.g., PCB) from uniform white backgrounds | Augment with colour jitter, random crops |
| Source imbalance      | FILL_IN class sourced mostly from DS1               | FILL_IN    |
| Geographic bias       | Images may be from non-Indian devices               | Supplement with own phone photos |
| Class coverage        | Only 6 e-waste classes (no printer, TV, etc.)       | Future work: expand classes |
| Single-object only    | Each image shows one device (no multi-object)       | Future work: object detection |

---

## Licence Summary

All source datasets must be verified individually (see Sources table).
Own photos (team-collected): CC BY 4.0 — attribution required.

> **Disclaimer:** This dataset is for academic research only. All images are
> used in good faith. If any source licence prohibits redistribution, do not
> upload the dataset publicly; share only model weights and manifests.

---

## Citation (fill in after verifying sources)

```
@dataset{ewaste_classifier_2026,
  title   = {E-Waste Classifier Dataset v1.0},
  author  = {FILL_IN TEAM NAMES},
  year    = {2026},
  note    = {Assembled from VERIFY sources. See dataset_card.md for details.}
}
```
