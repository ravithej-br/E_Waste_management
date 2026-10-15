# Streamlit Frontend UI (Phase 7)

Interactive web application for the **Lightweight EfficientNet-Based E-Waste Classification and Recycling Guidance System**.

---

## 1. How to Launch the Application

From the project root directory (`d:\e-waste`):

```powershell
& "C:\Users\RAVITHEJA B R\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run frontend/app.py
```

The Streamlit dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 2. Key User Interface Capabilities

1. **Dual Image Input Modes**:
   - **Upload File**: Select any JPG, PNG, or WebP photo up to 10 MB.
   - **Webcam Capture**: Take a real-time photo of physical e-waste items using your device camera.
   - **Quick Test Sample**: Instant testing dropdown loading genuine test images from `data/processed/test/`.
2. **Confidence Safeguard**:
   - Sliders allow tuning the safeguard threshold (default 0.65).
   - If confidence falls below 0.65, a cautionary banner appears with retake tips to prevent improper hazardous waste handling.
3. **Hazard Dossier & Handling**:
   - Color-coded badges: Critical (Red), High (Orange), Moderate (Yellow), Low (Green).
   - Chemical toxins table (Mercury, Lead, Lithium, PBDEs).
   - Dos and Don'ts for safe household segregation.
4. **Geographic Recycler Mapping**:
   - Proximity calculation (Haversine formula in km).
   - Interactive map showing the user location and closest KSPCB-licensed recycling facilities.
   - Recycler cards with direct phone numbers, email, physical addresses, and authorization IDs.
5. **Privacy Guarantee**:
   - Strictly in-memory image analysis via `io.BytesIO`. Zero files saved to disk.
