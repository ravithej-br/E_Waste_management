"""
frontend/app.py
───────────────
Streamlit Web Application:
Lightweight EfficientNet-Based E-Waste Classification and Recycling Guidance System.

Features:
  - Dual Mode: Standalone in-memory ONNX engine or FastAPI client
  - Camera capture and file upload
  - Calibrated confidence scoring (T=0.4923) with safety threshold interception (<0.65)
  - Color-coded hazard assessment under India E-Waste (Management) Rules 2022
  - Bengaluru KSPCB-authorized recycling facilities with Haversine distance and interactive map
  - Zero disk storage privacy guarantee
"""

import sys
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    TEMPERATURE,
    PROCESSED_DIR,
)
from src.utils.class_loader import get_class_names
from backend.inference import get_inference_engine
from backend.geo_service import get_nearest_centers, load_recyclers_db

# ─────────────────────────────────────────────
# PAGE CONFIGURATION & STYLES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="E-Waste AI Classifier & Recycling Guidance",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1b4d3e 0%, #006644 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #e0f2fe;
        margin: 5px 0 0 0;
        font-size: 1.05rem;
    }
    .hazard-badge-critical {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #f87171;
    }
    .hazard-badge-high {
        background-color: #ffedd5;
        color: #9a3412;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #fb923c;
    }
    .hazard-badge-moderate {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #facc15;
    }
    .hazard-badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #4ade80;
    }
    .recycler-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .privacy-callout {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 15px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# BENGALURU GPS PRESETS
# ─────────────────────────────────────────────
BLR_PRESETS = {
    "Central Bengaluru (Vidhana Soudha / Majestic)": (12.9716, 77.5946),
    "Electronic City (Phase 1 & 2)": (12.8452, 77.6602),
    "Whitefield / ITPL": (12.9850, 77.7315),
    "Koramangala": (12.9352, 77.6245),
    "Indiranagar": (12.9784, 77.6408),
    "Peenya Industrial Area": (13.0285, 77.5197),
    "Yelahanka / North Bengaluru": (13.1007, 77.5963),
    "Custom GPS Coordinates": None,
}


# ─────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/recycle.png", width=64)
    st.title("Settings & Controls")

    st.subheader("1. Location in Bengaluru")
    selected_preset = st.selectbox("Select Bengaluru Region", list(BLR_PRESETS.keys()), index=0)

    if selected_preset == "Custom GPS Coordinates":
        u_lat = st.number_input("Latitude", value=12.9716, format="%.4f")
        u_lon = st.number_input("Longitude", value=77.5946, format="%.4f")
    else:
        coords = BLR_PRESETS[selected_preset]
        u_lat, u_lon = coords[0], coords[1]
        st.caption(f"Coordinates: `{u_lat:.4f}, {u_lon:.4f}`")

    st.divider()

    st.subheader("2. Safety Threshold")
    threshold = st.slider(
        "Confidence Safeguard Cutoff",
        min_value=0.50,
        max_value=0.90,
        value=float(DEFAULT_CONFIDENCE_THRESHOLD),
        step=0.05,
        help="Predictions below this cutoff trigger safety interception to prevent dangerous handling errors.",
    )

    st.divider()

    st.subheader("3. Academic Project Info")
    st.markdown(
        """
        - **Institution:** Bengaluru, Karnataka
        - **Model:** EfficientNet-B0 (INT8 Quantized)
        - **Accuracy:** 90.07% (Test Set)
        - **Latency:** ~5.0 ms ONNX CPU
        - **Calibration:** Temperature Scaling ($T=0.4923$)
        """
    )


# ─────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>♻️ Lightweight E-Waste Classification & Recycling Guidance</h1>
        <p>AI-Powered Hazard Detection, Legal Compliance under India E-Waste Rules 2022, and Bengaluru Recycling Locator</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Privacy Callout Banner
st.markdown(
    """
    <div class="privacy-callout">
        🔒 <b>Zero Disk Storage Privacy Guarantee:</b> Your uploaded or captured photo is processed strictly in volatile RAM and is never stored on disk or shared with external parties.
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# TABS INTERFACE
# ─────────────────────────────────────────────
tab_scan, tab_directory, tab_legal, tab_system = st.tabs(
    ["📸 Scan & Classify", "🏢 Recyclers Directory", "⚖️ India E-Waste Laws", "⚙️ Architecture & Benchmarks"]
)


# ─────────────────────────────────────────────
# TAB 1: SCAN & CLASSIFY
# ─────────────────────────────────────────────
with tab_scan:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("Input Image")
        input_mode = st.radio(
            "Select Input Source:",
            ["📁 Upload File", "📷 Live Camera", "🧪 Quick Sample"],
            horizontal=True,
        )

        image_bytes = None
        preview_img = None

        if input_mode == "📁 Upload File":
            uploaded_file = st.file_uploader(
                "Upload e-waste photo (JPG, PNG, WebP)",
                type=["jpg", "jpeg", "png", "webp"],
            )
            if uploaded_file is not None:
                image_bytes = uploaded_file.getvalue()
                preview_img = Image.open(io.BytesIO(image_bytes))

        elif input_mode == "📷 Live Camera":
            camera_file = st.camera_input("Capture photo using webcam")
            if camera_file is not None:
                image_bytes = camera_file.getvalue()
                preview_img = Image.open(io.BytesIO(image_bytes))

        elif input_mode == "🧪 Quick Sample":
            test_dir = PROCESSED_DIR / "test"
            sample_options = {}
            if test_dir.exists():
                for cls_dir in sorted(test_dir.iterdir()):
                    if cls_dir.is_dir():
                        imgs = list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png"))
                        if imgs:
                            sample_options[f"{cls_dir.name} (sample)"] = imgs[0]

            if sample_options:
                selected_sample = st.selectbox("Choose a test dataset sample:", list(sample_options.keys()))
                sample_path = sample_options[selected_sample]
                preview_img = Image.open(sample_path)
                buf = io.BytesIO()
                preview_img.save(buf, format="JPEG")
                image_bytes = buf.getvalue()
            else:
                st.info("No test samples found in data/processed/test.")

        if preview_img is not None:
            st.image(preview_img, caption="Source Image Preview", use_container_width=True)

    with col_output:
        st.subheader("Classification & Guidance")

        if image_bytes is None:
            st.info("👈 Upload an image, capture with webcam, or select a sample to see analysis.")
        else:
            with st.spinner("Analyzing with ONNX Runtime Engine..."):
                try:
                    engine = get_inference_engine()
                    res = engine.predict(
                        image_bytes=image_bytes,
                        threshold=threshold,
                        user_lat=u_lat,
                        user_lon=u_lon,
                    )
                except Exception as e:
                    st.error(f"Inference error: {e}")
                    res = None

            if res is not None:
                pred_label = res["prediction"]
                calib_conf = res["calibrated_confidence"]
                is_confident = res["is_confident"]
                guidance = res["guidance"]
                top_3 = res["top_3"]
                recyclers = res["nearest_recyclers"]
                latency = res["latency_ms"]

                # ── Top-1 Class & Confidence Header ──
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    st.metric(
                        label="Predicted E-Waste Class",
                        value=pred_label.replace("_", " ").upper(),
                    )
                with col_c2:
                    st.metric(
                        label="Calibrated Confidence",
                        value=f"{calib_conf * 100:.1f}%",
                        delta=f"Threshold: {threshold * 100:.0f}%",
                    )

                # Confidence Bar
                st.progress(min(max(float(calib_conf), 0.0), 1.0))

                # ── Safeguard Warning Banner ──
                if not is_confident or guidance.get("status") == "uncertain":
                    st.warning(
                        f"""
                        ⚠️ **Confidence Safeguard Activated!**
                        The model's calibrated confidence ({calib_conf*100:.1f}%) is below the safety threshold ({threshold*100:.0f}%).
                        
                        **Action Recommended:**
                        - Do not dispose of this object based on preliminary prediction.
                        - Retake photo with the object centered and well-lit.
                        - Avoid extreme angles or cluttered backgrounds.
                        """
                    )
                else:
                    st.success("✅ Prediction exceeds safety threshold. High reliability.")

                # ── Top-3 Probabilities ──
                st.markdown("##### Top-3 Candidate Classes")
                df_top3 = pd.DataFrame(top_3)
                df_top3["confidence_pct"] = (df_top3["confidence"] * 100).round(1)
                st.bar_chart(
                    data=df_top3.set_index("label")["confidence_pct"],
                    color="#006644",
                )

                # ── Hazard & Handling Dossier ──
                st.markdown("---")
                hazard_level = guidance.get("hazard_level", "UNKNOWN").upper()
                badge_class = "hazard-badge-moderate"
                if "CRITICAL" in hazard_level:
                    badge_class = "hazard-badge-critical"
                elif "HIGH" in hazard_level:
                    badge_class = "hazard-badge-high"
                elif "LOW" in hazard_level:
                    badge_class = "hazard-badge-low"

                st.markdown(
                    f"#### Hazard Assessment: <span class='{badge_class}'>{hazard_level}</span>",
                    unsafe_allow_html=True,
                )

                if "chemical_hazards" in guidance:
                    st.markdown("**🧪 Toxic Compounds Identified:**")
                    chemicals = guidance["chemical_hazards"]
                    st.write(", ".join([f"`{c}`" for c in chemicals]))

                if "safe_handling" in guidance:
                    with st.expander("🛡️ Safe Handling Procedures & Precautions", expanded=True):
                        handling = guidance["safe_handling"]
                        if "dos" in handling:
                            st.markdown("**Recommended Actions (DO):**")
                            for do_item in handling["dos"]:
                                st.markdown(f"- ✅ {do_item}")
                        if "donts" in handling:
                            st.markdown("**Prohibited Actions (DON'T):**")
                            for dont_item in handling["donts"]:
                                st.markdown(f"- ❌ {dont_item}")
                        if "emergency" in handling:
                            st.markdown(f"**🚨 Emergency Note:** {handling['emergency']}")

                if "legal_compliance" in guidance:
                    st.info(f"⚖️ **Regulatory Mandate:** {guidance['legal_compliance'].get('primary_regulation', 'India E-Waste Rules 2022')}")

                # ── Nearest Recyclers Section ──
                st.markdown("---")
                st.markdown(f"#### 📍 Nearest Bengaluru Recycling Centers for `{pred_label}`")

                if recyclers:
                    # Prepare map coordinates
                    map_points = [
                        {"lat": u_lat, "lon": u_lon, "type": "You", "name": "Your Selected Location"}
                    ]
                    for idx, c in enumerate(recyclers, 1):
                        c_coord = c["coordinates"]
                        map_points.append({
                            "lat": c_coord["lat"],
                            "lon": c_coord["lon"],
                            "type": "Recycler",
                            "name": f"#{idx} {c['name']} ({c['distance_km']} km)"
                        })

                        with st.container():
                            st.markdown(
                                f"""
                                <div class="recycler-card">
                                    <h4 style="margin: 0 0 6px 0; color: #006644;">#{idx} {c['name']} — <span style="color: #0284c7;">{c['distance_km']} km away</span></h4>
                                    <p style="margin: 0 0 4px 0;"><b>Address:</b> {c['address']}</p>
                                    <p style="margin: 0 0 4px 0;"><b>Contact Phone:</b> {c['phone']} | <b>Email:</b> {c['email']}</p>
                                    <p style="margin: 0 0 4px 0;"><b>KSPCB Authorization:</b> <code>{c['kspcb_auth_no']}</code></p>
                                    <p style="margin: 0; font-size: 0.9em; color: #475569;"><b>Accepted:</b> {', '.join(c['categories_accepted'])}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    # Interactive Map
                    df_map = pd.DataFrame(map_points)
                    st.map(df_map, latitude="lat", longitude="lon", size=20, zoom=11)

                else:
                    st.info("No specific centers found accepting this material class.")

                # Latency & Model Footprint
                st.caption(
                    f"⚡ Model: `{res['model_info']['name']}` | Preprocess: `{latency['preprocess']} ms` | "
                    f"Inference: `{latency['inference']} ms` | Total: `{latency['total']} ms`"
                )


# ─────────────────────────────────────────────
# TAB 2: RECYCLERS DIRECTORY
# ─────────────────────────────────────────────
with tab_directory:
    st.subheader("Authorized E-Waste Recyclers & Collection Centers (Bengaluru)")
    st.markdown("Official KSPCB/CPCB registered recycling facilities in Bengaluru, Karnataka.")

    all_centers = load_recyclers_db()
    classes = get_class_names()

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        cat_filter = st.selectbox("Filter by Material Accepted:", ["All Categories"] + classes)
    with col_f2:
        search_query = st.text_input("Search facility name or location:")

    filtered = []
    for c in all_centers:
        if cat_filter != "All Categories" and cat_filter not in c["categories_accepted"]:
            continue
        if search_query and search_query.lower() not in c["name"].lower() and search_query.lower() not in c["address"].lower():
            continue
        filtered.append(c)

    st.write(f"Showing **{len(filtered)}** facilities:")

    for c in filtered:
        with st.expander(f"🏢 {c['name']} — {c.get('area', 'Bengaluru')}"):
            st.write(f"**Address:** {c['address']}")
            st.write(f"**Phone:** {c['phone']} | **Email:** {c['email']}")
            st.write(f"**KSPCB Auth No:** `{c['kspcb_auth_no']}`")
            st.write(f"**Accepted Categories:** {', '.join(c['categories_accepted'])}")
            st.write(f"**Coordinates:** `{c['coordinates']['lat']}, {c['coordinates']['lon']}`")


# ─────────────────────────────────────────────
# TAB 3: INDIA E-WASTE LAWS
# ─────────────────────────────────────────────
with tab_legal:
    st.subheader("Legal & Regulatory Framework (Government of India)")

    st.markdown(
        """
        ### 1. E-Waste (Management) Rules, 2022
        Notified by the Ministry of Environment, Forest and Climate Change (MoEFCC) via GSR 816(E) on 2nd November 2022, replacing the 2016 rules.

        - **Extended Producer Responsibility (EPR):** Mandates producers to meet quantified recycling targets for all electronics placed on the market.
        - **Prohibition of Informal Burning:** Open burning or acid leaching of PCBs, cables, and cathode-ray tubes is strictly illegal.
        - **Penalty Clause:** Violations are punishable under **Section 15 of the Environment (Protection) Act, 1986** (imprisonment up to 5 years, fine up to ₹1,00,000, or both).

        ---

        ### 2. Battery Waste Management Rules, 2022
        Notified under GSR 664(E) on 22nd August 2022:
        - Covers all battery chemistries (Lithium-ion, Lead-acid, Nickel-cadmium, Alkaline).
        - 100% recovery and recycling mandate for materials (Cobalt, Lithium, Nickel, Lead).
        - Prohibits disposal in municipal landfills or municipal waste streams.

        ---

        ### 3. Material Hazard Matrix
        """
    )

    hazard_table = [
        {"Component": "Battery (Li-ion / Lead-Acid)", "Key Toxins": "Cobalt, Lithium, Sulfuric Acid, Lead", "Risk": "Thermal runaway, groundwater heavy metal leaching", "Statutory Rule": "Battery Waste Rules 2022"},
        {"Component": "CFL / Mercury Lamp", "Key Toxins": "Mercury vapor, fluorescent powder", "Risk": "Neurotoxicity upon inhalation of broken phosphor", "Statutory Rule": "E-Waste Rules 2022 Schedule I"},
        {"Component": "CRT Monitor", "Key Toxins": "Lead oxide funnel glass, Barium", "Risk": "Implosion hazard, 1-2 kg lead per tube", "Statutory Rule": "E-Waste Rules 2022 Schedule I"},
        {"Component": "Printed Circuit Board (PCB)", "Key Toxins": "Brominated flame retardants (PBDEs), Lead-tin solder", "Risk": "Dioxin emission during improper burning", "Statutory Rule": "E-Waste Rules 2022 Schedule I"},
        {"Component": "Mobile Phone", "Key Toxins": "Lithium, Gold, Tantalum, Trace Arsenic", "Risk": "Resource depletion, fire hazard from battery", "Statutory Rule": "E-Waste Rules 2022 Schedule I"},
        {"Component": "Keyboard / Peripherals", "Key Toxins": "ABS plastics, Polybrominated biphenyls", "Risk": "Microplastic contamination, persistent flame retardants", "Statutory Rule": "E-Waste Rules 2022 Schedule I"},
    ]
    st.table(pd.DataFrame(hazard_table))


# ─────────────────────────────────────────────
# TAB 4: ARCHITECTURE & BENCHMARKS
# ─────────────────────────────────────────────
with tab_system:
    st.subheader("System Architecture & Empirical Benchmarks")

    st.markdown(
        """
        #### 1. Machine Learning Pipeline
        - **Backbone Architecture:** EfficientNet-B0 (5.3M parameters, 224x224 input)
        - **Alternative Tested:** MobileNetV3-Small (1.5M parameters)
        - **Transfer Learning Strategy:** 2-Stage Training (Head-only 5 epochs, Top blocks fine-tuning 10 epochs with Cosine Annealing)
        - **Calibration:** Post-hoc Temperature Scaling ($T=0.4923$), reducing Expected Calibration Error (ECE) from 20.20% to 2.89% (85.7% reduction).
        - **Inference Optimization:** Selective Production INT8 ONNX Quantization preserving depthwise separable convolutions in FP32.
        """
    )

    col_b1, col_b2 = st.columns([1, 1])

    with col_b1:
        st.markdown("##### Test Accuracy Comparison")
        acc_data = {
            "Model Variant": ["EfficientNet-B0 (PyTorch FP32)", "EfficientNet-B0 (Selective ONNX INT8)", "MobileNetV3-Small (PyTorch FP32)"],
            "Test Accuracy": ["90.22%", "90.07%", "88.35%"],
            "Model Size (MB)": ["15.61 MB", "15.29 MB", "5.95 MB"],
            "Hazard Class Recall": ["100.0%", "100.0%", "100.0%"]
        }
        st.table(pd.DataFrame(acc_data))

    with col_b2:
        st.markdown("##### Latency Benchmarks (CPU - 100 Trials)")
        latency_data = {
            "Execution Mode": ["PyTorch FP32 Baseline", "ONNX FP32 Engine", "ONNX Selective INT8 Engine", "MobileNetV3 ONNX FP32"],
            "Preprocessing Latency": ["3.46 ms", "3.46 ms", "3.46 ms", "3.46 ms"],
            "Inference Latency": ["21.28 ms", "5.03 ms", "5.03 ms", "1.49 ms"],
            "Total Pipeline": ["24.74 ms", "8.49 ms", "8.49 ms", "4.95 ms"]
        }
        st.table(pd.DataFrame(latency_data))

    st.caption("All benchmarks measured locally on Windows x64 Intel/AMD CPU with single-batch inference.")


# ─────────────────────────────────────────────
# FOOTER & LEGAL DISCLAIMER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0;">
        ⚠️ <b>Disclaimer:</b> This application is an educational CSE mini-project developed in Bengaluru, Karnataka.
        Guidance provided is informational and does not replace formal certification or KSPCB hazardous waste manifests.
        Always deliver electronic waste to authorized collection centers.
    </div>
    """,
    unsafe_allow_html=True,
)
