# EcoScan AI - Frontend Portal

Modern, multi-page web application for the **Lightweight EfficientNet-Based E-Waste Classification and Recycling Guidance System**.

---

## 1. Quick Launch

From the project root directory (`d:\e-waste`):

```powershell
& "C:\Users\RAVITHEJA B R\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run frontend/app.py
```

The application will open in your default browser at **`http://localhost:8501`**.

---

## 2. Authentication & User Access

- **Sign In / Registration**: Create an account with your Name, Email, and Password.
- **1-Click Demo Access**: Click `⚡ One-Click Demo Mode (Tester Access)` to sign in immediately as `demo`.
  - **Demo Username:** `demo`
  - **Demo Password:** `demo123`

---

## 3. Dedicated Pages Architecture

1. **📸 Scanner & Classifier (`frontend/views/scanner.py`)**:
   - In-memory INT8 ONNX forward pass with ImageNet normalization.
   - Temperature scaling ($T=0.4923$) and confidence safeguard alerts ($<0.65$).
   - Top-3 candidate distribution bar chart.
   - Chemical toxins table and statutory handling Dos & Don'ts.
   - Automatically logs scan audits to user account history.
2. **📍 Recyclers Directory (`frontend/views/recyclers.py`)**:
   - Interactive map plotting user coordinates and 8 certified KSPCB recycling centers across Bengaluru.
   - Haversine proximity distance calculation in kilometers.
   - Direct phone, email, address, and license ID cards.
3. **⚖️ Legal Guidelines (`frontend/views/regulations.py`)**:
   - Comprehensive statutory overview of India E-Waste (Management) Rules 2022 and Battery Waste Rules 2022.
   - Chemical hazard matrix, EPR obligations, and Section 15 Environment (Protection) Act penalties.
4. **📊 Model Benchmarks (`frontend/views/benchmarks.py`)**:
   - Test set accuracy (90.07% Selective INT8), CPU latency breakdown (5.03 ms), and calibration error reduction.
5. **👤 Account & History (`frontend/views/profile.py`)**:
   - User profile credentials and interactive table of previous scans with timestamps and hazard ratings.
