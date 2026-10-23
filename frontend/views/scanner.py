"""
frontend/views/scanner.py
─────────────────────────
Modern AI E-Waste Scanner and Classifier view.
Provides image capture/upload, in-memory ONNX inference, temperature-calibrated scoring,
hazard assessment, and automated scan history recording.
"""

import io
from pathlib import Path
from PIL import Image
import streamlit as st
import pandas as pd

from config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    PROCESSED_DIR,
)
from backend.inference import get_inference_engine
from frontend.auth import record_scan


def render_scanner_page():
    """Renders the dedicated scanner and classification interface."""
    st.markdown(
        """
        <div class="hero-banner">
            <h1>📸 Intelligent E-Waste Scanner</h1>
            <p>Upload or capture high-resolution electronic scrap to assess hazard class, toxins, and disposal protocols.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar parameters
    with st.sidebar:
        st.markdown("### 🎛️ Scanner Settings")
        threshold = st.slider(
            "Confidence Safety Threshold",
            min_value=0.50,
            max_value=0.90,
            value=float(DEFAULT_CONFIDENCE_THRESHOLD),
            step=0.05,
            help="Predictions below this cutoff trigger precautionary alerts under statutory rules."
        )
        st.caption(f"Default calibrated cutoff: `{DEFAULT_CONFIDENCE_THRESHOLD}`")

    # Main layout
    col_input, col_result = st.columns([1, 1.2], gap="large")

    image_bytes = None
    preview_img = None

    with col_input:
        st.markdown("### 1. Select Input Source")
        input_tab1, input_tab2, input_tab3 = st.tabs(["📁 File Upload", "📷 Live Webcam", "🧪 Test Dataset"])

        with input_tab1:
            uploaded_file = st.file_uploader(
                "Upload e-waste photo (JPG, PNG, WebP up to 10MB)",
                type=["jpg", "jpeg", "png", "webp"],
                key="uploader",
            )
            if uploaded_file is not None:
                image_bytes = uploaded_file.getvalue()
                preview_img = Image.open(io.BytesIO(image_bytes))

        with input_tab2:
            camera_file = st.camera_input("Capture item with device camera", key="webcam")
            if camera_file is not None:
                image_bytes = camera_file.getvalue()
                preview_img = Image.open(io.BytesIO(image_bytes))

        with input_tab3:
            test_dir = PROCESSED_DIR / "test"
            sample_options = {}
            if test_dir.exists():
                for cls_dir in sorted(test_dir.iterdir()):
                    if cls_dir.is_dir():
                        imgs = list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png"))
                        if imgs:
                            sample_options[f"{cls_dir.name.replace('_', ' ').title()}"] = imgs[0]

            if sample_options:
                selected_sample = st.selectbox("Choose preloaded test benchmark sample:", list(sample_options.keys()))
                sample_path = sample_options[selected_sample]
                preview_img = Image.open(sample_path)
                buf = io.BytesIO()
                preview_img.save(buf, format="JPEG")
                image_bytes = buf.getvalue()
            else:
                st.info("Test dataset partition not found.")

        if preview_img is not None:
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 12px; margin-top: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                """,
                unsafe_allow_html=True,
            )
            st.image(preview_img, caption="Loaded Image Preview (Processed in RAM)", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with col_result:
        st.markdown("### 2. Neural Classification & Risk Dossier")

        if image_bytes is None:
            st.markdown(
                """
                <div style="background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 48px 24px; text-align: center; color: #64748b;">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
                    <h4 style="color: #334155; margin-bottom: 6px;">No Image Loaded Yet</h4>
                    <p style="font-size: 0.95rem; margin: 0;">Upload a photo or choose a test sample on the left to initiate real-time ONNX inference.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            with st.spinner("Executing INT8 ONNX forward pass & calibrating logits..."):
                try:
                    engine = get_inference_engine()
                    res = engine.predict(
                        image_bytes=image_bytes,
                        threshold=threshold,
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
                latency = res["latency_ms"]

                # Automatically log scan to user's history
                user_info = st.session_state.get("user")
                if user_info and "username" in user_info:
                    record_scan(
                        username=user_info["username"],
                        prediction=pred_label,
                        confidence=calib_conf,
                        hazard_level=guidance.get("hazard_level", "MODERATE"),
                    )

                # Determine badge styling
                hazard_level = guidance.get("hazard_level", "MODERATE").upper()
                badge_class = "badge-moderate"
                if "CRITICAL" in hazard_level:
                    badge_class = "badge-critical"
                elif "HIGH" in hazard_level:
                    badge_class = "badge-high"
                elif "LOW" in hazard_level:
                    badge_class = "badge-low"

                # Top Result Card
                st.markdown(
                    f"""
                    <div class="modern-card fade-in-container">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <div>
                                <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 600;">Identified Classification</span>
                                <h2 style="margin: 2px 0 0 0; font-size: 1.8rem; color: #0f172a; font-weight: 800;">
                                    {pred_label.replace('_', ' ').title()}
                                </h2>
                            </div>
                            <span class="{badge_class}">
                                {hazard_level}
                            </span>
                        </div>
                        <div style="margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.9rem; font-weight: 600; margin-bottom: 6px;">
                                <span style="color: #334155;">Calibrated Confidence (T=0.4923):</span>
                                <span style="color: {'#059669' if is_confident else '#dc2626'};">{calib_conf * 100:.1f}%</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.progress(min(max(float(calib_conf), 0.0), 1.0))

                # Safeguard Alert if below cutoff
                if not is_confident or guidance.get("status") == "uncertain":
                    st.markdown(
                        f"""
                        <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 14px 18px; border-radius: 8px; margin-bottom: 16px;">
                            <div style="font-weight: 700; color: #b45309; margin-bottom: 4px;">⚠️ Statutory Confidence Safeguard Active</div>
                            <div style="font-size: 0.9rem; color: #92400e;">
                                Calibrated probability ({calib_conf*100:.1f}%) is below the safety threshold ({threshold*100:.0f}%).
                                Avoid physical dismantling or disposal based on this unverified result. Retake under proper lighting with the item centered.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; font-size: 0.88rem; color: #047857; font-weight: 600;">
                            ✅ High confidence classification. Compliant with safe categorization protocols.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Candidate Top-3 distribution
                st.markdown("##### Probabilistic Distribution (Top 3)")
                df_top3 = pd.DataFrame(top_3)
                df_top3["Confidence (%)"] = (df_top3["confidence"] * 100).round(1)
                df_top3["Class"] = df_top3["label"].apply(lambda s: s.replace("_", " ").title())
                st.bar_chart(
                    data=df_top3.set_index("Class")["Confidence (%)"],
                    color="#059669",
                )

                # Toxic compounds
                if "chemical_hazards" in guidance:
                    st.markdown("##### 🧪 Identified Hazardous Chemical Compounds")
                    chems = guidance["chemical_hazards"]
                    chem_tags = " ".join([f"<span style='background: #f1f5f9; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; color: #334155; margin-right: 6px;'>{c}</span>" for c in chems])
                    st.markdown(f"<div style='margin-bottom: 16px;'>{chem_tags}</div>", unsafe_allow_html=True)

                # Handling Dossier
                if "safe_handling" in guidance:
                    with st.expander("🛡️ Statutory Handling Procedures (Dos & Don'ts)", expanded=True):
                        h = guidance["safe_handling"]
                        if "dos" in h:
                            st.markdown("**Mandatory Precautions (DO):**")
                            for d in h["dos"]:
                                st.markdown(f"- ✅ {d}")
                        if "donts" in h:
                            st.markdown("**Strictly Prohibited (DON'T):**")
                            for dt in h["donts"]:
                                st.markdown(f"- ❌ {dt}")
                        if "emergency" in h:
                            st.error(f"🚨 **Emergency Action:** {h['emergency']}")

                # Latency & Model Info
                st.caption(
                    f"⚡ Model: `{res['model_info']['name']}` | Preprocess: `{latency['preprocess']} ms` | "
                    f"Inference: `{latency['inference']} ms` | Total: `{latency['total']} ms` (RAM Only)"
                )
