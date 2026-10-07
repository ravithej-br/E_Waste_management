# Phone Photo Collection Guide
# For team members collecting their own e-waste images
# ─────────────────────────────────────────────────────

## Target: 30+ photos per under-represented class

## How to shoot good photos

### Equipment
- Any smartphone camera (10 MP+ preferred)
- No special lighting required — vary it intentionally

### For each item, take photos with:
1. Clean background (white table) — 30%
2. Cluttered background (desk with other items) — 40%
3. Outdoor / natural light — 20%
4. Low light / shadowed — 10%

### Angles:
- Front face
- Side view
- Top-down (45-degree angle)
- Close-up of labels/ports

### Settings:
- Shoot in JPEG or PNG
- Minimum 640x640 pixels
- Do NOT use filters or heavy post-processing

## Naming convention
Save as: `own_<class>_<yourname>_<001>.jpg`
Example:  `own_battery_ravi_001.jpg`
          `own_mobile_phone_priya_003.jpg`

## Where to put them
Place in:  data/raw/downloads/own_photos/<class_name>/

The ingest.py script will pick them up if you add "own_photos" entries
to CLASS_MAPPING in src/dataset/ingest.py.

## What to photograph (examples)

| Class        | Items to photograph |
|--------------|---------------------|
| battery      | AA, AAA, 9V, lithium coin cells, power bank batteries (removed) |
| cfl_bulb     | Spiral CFL, tube CFL (do NOT break — mercury hazard!) |
| keyboard     | USB keyboard, laptop keyboard (detached), wireless keyboard |
| mobile_phone | Old smartphones, feature phones (not currently-used devices!) |
| monitor_crt  | Old CRT monitors, CRT TVs (if available — rare, check with family/friends) |
| pcb          | Old motherboards, graphics cards, RAM sticks, hard drive PCBs |
| other        | Paper, plastic bottles, food containers, books (non-e-waste items) |

## Privacy
- Do NOT photograph people or their personal data/screens.
- Remove SIM cards and wipe storage before photographing phones.
- Do NOT upload photos to public repos — keep in data/ (gitignored).

## Minimum viable per class
- 80 images total per class (from all sources combined).
- Aim for 20+ own photos if a class is below this threshold.
