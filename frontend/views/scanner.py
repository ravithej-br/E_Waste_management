"""
frontend/views/scanner.py
─────────────────────────
Modern, interactive AI E-Waste Scanner.
Features clear upload/camera controls, explicit action buttons,
high-contrast dark-mode cards, and streamlined hazard dossiers.
"""

import io
from PIL import Image
import streamlit as st

from config import DEFAULT_CONFIDENCE_THRESHOLD
from backend.inference import get_inference_engine
from frontend.auth import record_scan

CLASS_ICONS = {
    "battery": "🔋",
    "cfl_bulb": "💡",
    "keyboard": "⌨️",
    "mobile_phone": "📱",
    "monitor_crt": "🖥️",
    "pcb": "🔌",
    "other": "📦",
}

CLASS_DISPLAY = {
    "battery": "Battery (Li-ion / Lead-Acid)",
    "cfl_bulb": "CFL / Mercury Lamp Bulb",
    "keyboard": "Computer Keyboard / Peripheral",
    "mobile_phone": "Smartphone / Mobile Phone",
    "monitor_crt": "Cathode Ray Tube (CRT) Monitor",
    "pcb": "Printed Circuit Board (PCB)",
    "other": "Unclassified E-Waste",
}


def render_scanner_page():
    """Renders the simplified, action-driven scanner interface."""
    # Header
    st.markdown(
        """
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>📸 E-Waste Neural Scanner</h1>
                    <p>Instant material identification, hazard safety ratings, and disposal guidance.</p>
                </div>
                <div class="privacy-tag">
                    🔒 Volatile RAM Only • Zero Disk Storage
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar settings
    with st.sidebar:
        st.markdown("### ⚙️ Scanner Sensitivity")
        threshold = st.slider(
            "Confidence Cutoff",
            min_value=0.50,
            max_value=0.90,
            value=float(DEFAULT_CONFIDENCE_THRESHOLD),
            step=0.05,
            help="Images with confidence below this threshold trigger precautionary warnings."
        )
        st.caption(f"Statutory calibrated cutoff: **{threshold:.2f}**")

    # Initialize scan state
    if "active_image_bytes" not in st.session_state:
        st.session_state["active_image_bytes"] = None
    if "current_scan_result" not in st.session_state:
        st.session_state["current_scan_result"] = None

    col_upload, col_analysis = st.columns([1, 1.2], gap="large")

    with col_upload:
        st.markdown("### 1. Provide Photo")

        input_choice = st.radio(
            "Choose Input Method:",
            ["📁 Upload Photo", "📷 Use Camera"],
            horizontal=True,
            label_visibility="collapsed",
        )

        loaded_bytes = None
        preview_pil = None

        if input_choice == "📁 Upload Photo":
            up_file = st.file_uploader(
                "Upload JPG, PNG, or WebP photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="file_uploader",
                help="Select an e-waste photo from your computer."
            )
            if up_file is not None:
                loaded_bytes = up_file.getvalue()
                preview_pil = Image.open(io.BytesIO(loaded_bytes))
        else:
            cam_file = st.camera_input("Capture with device camera", key="cam_input")
            if cam_file is not None:
                loaded_bytes = cam_file.getvalue()
                preview_pil = Image.open(io.BytesIO(loaded_bytes))

        # Update session image
        if loaded_bytes != st.session_state["active_image_bytes"]:
            st.session_state["active_image_bytes"] = loaded_bytes
            # Reset scan result when image changes
            st.session_state["current_scan_result"] = None

        if preview_pil is not None:
            # Framing Zoom Control
            zoom_val = st.select_slider(
                "🔍 Framing Focus & Zoom:",
                options=[1.0, 1.2, 1.3, 1.5],
                value=1.0,
                format_func=lambda z: f"{z}x (Close-up Focus)" if z > 1.0 else "1.0x (Full Frame)",
                help="Zoom in to crop out wide table surfaces, glare, and background reflections."
            )

            # Apply Zoom if selected
            processed_bytes = loaded_bytes
            if zoom_val > 1.0:
                w, h = preview_pil.size
                cw, ch = int(w / zoom_val), int(h / zoom_val)
                left, top = (w - cw) // 2, (h - ch) // 2
                preview_pil = preview_pil.crop((left, top, left + cw, top + ch))
                buf = io.BytesIO()
                preview_pil.save(buf, format="JPEG")
                processed_bytes = buf.getvalue()

            st.image(preview_pil, caption=f"Active Viewfinder ({zoom_val}x framing)", use_container_width=True)

            # Prominent Action Button
            analyze_clicked = st.button(
                "⚡ Analyze & Classify E-Waste",
                type="primary",
                use_container_width=True,
                key="btn_analyze"
            )

            st.caption("💡 **Tip:** If the item is small or has table glare/reflections, use **1.2x or 1.3x Zoom** to focus on the object.")

            if analyze_clicked:
                with st.spinner("Classifying image with INT8 ONNX Engine..."):
                    try:
                        engine = get_inference_engine()
                        res = engine.predict(
                            image_bytes=processed_bytes,
                            threshold=threshold,
                        )
                        st.session_state["current_scan_result"] = res

                        # Record scan in database
                        user_info = st.session_state.get("user")
                        if user_info and "username" in user_info:
                            record_scan(
                                username=user_info["username"],
                                prediction=res["prediction"],
                                confidence=res["calibrated_confidence"],
                                hazard_level=res["guidance"].get("hazard_level", "MODERATE"),
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Inference failed: {str(e)}")

    with col_analysis:
        st.markdown("### 2. Classification Results")

        res = st.session_state.get("current_scan_result")

        if res is None:
            if preview_pil is None:
                st.markdown(
                    """
                    <div class="dark-card" style="text-align: center; padding: 48px 24px; color: #94a3b8;">
                        <div style="font-size: 2.8rem; margin-bottom: 12px;">📸</div>
                        <h4 style="color: #ffffff; margin-bottom: 6px;">No Image Selected</h4>
                        <p style="font-size: 0.95rem; margin: 0; color: #94a3b8;">
                            Upload a photo or snap a picture on the left to start.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="dark-card" style="text-align: center; padding: 40px 20px; border-color: rgba(16, 185, 129, 0.4) !important;">
                        <div style="font-size: 2.5rem; margin-bottom: 8px;">👉</div>
                        <h3 style="color: #ffffff; margin-bottom: 6px;">Image Loaded!</h3>
                        <p style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 14px;">
                            Click the green <b>Analyze & Classify E-Waste</b> button to run the AI engine.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            # Result exists!
            pred = res["prediction"]
            conf = res["calibrated_confidence"]
            is_conf = res["is_confident"]
            guidance = res["guidance"]
            top_3 = res["top_3"]
            latency = res["latency_ms"]

            icon = CLASS_ICONS.get(pred, "📦")
            display_name = CLASS_DISPLAY.get(pred, pred.replace("_", " ").title())
            hazard_level = guidance.get("hazard_level", "MODERATE").upper()

            # Badge class
            badge_cls = "badge-moderate"
            if "CRITICAL" in hazard_level:
                badge_cls = "badge-critical"
            elif "HIGH" in hazard_level:
                badge_cls = "badge-high"
            elif "LOW" in hazard_level:
                badge_cls = "badge-low"

            # Primary Result Card
            st.markdown(
                f"""
                <div class="dark-card fade-in">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 2.2rem;">{icon}</span>
                            <div>
                                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 600;">Detected Category</span>
                                <h2 style="margin: 0; font-size: 1.5rem; color: #ffffff; font-weight: 800;">{display_name}</h2>
                            </div>
                        </div>
                        <span class="{badge_cls}">{hazard_level}</span>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 500;">AI Confidence Match:</span>
                        <span style="color: {'#10b981' if is_conf else '#f87171'}; font-weight: 800; font-size: 1.25rem;">
                            {conf * 100:.1f}%
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Warning if uncertain
            if not is_conf or guidance.get("status") == "uncertain":
                st.markdown(
                    f"""
                    <div style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 8px; margin-bottom: 14px;">
                        <div style="font-weight: 700; color: #fbbf24; font-size: 0.9rem;">⚠️ Precautionary Safeguard Active</div>
                        <div style="color: #fde68a; font-size: 0.85rem; margin-top: 2px;">
                            Confidence is below {threshold*100:.0f}%. If the object is blurred or partially obscured, please retake the photo with better lighting.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Top 3 Candidates (Modern horizontal bars)
            st.markdown("##### Candidate Predictions")
            bars_html = ""
            for item in top_3:
                c_name = item["label"]
                c_icon = CLASS_ICONS.get(c_name, "📦")
                c_disp = CLASS_DISPLAY.get(c_name, c_name.replace("_", " ").title())
                c_pct = round(item["confidence"] * 100, 1)
                bars_html += f"""
                <div class="candidate-row">
                    <span class="candidate-row-name">{c_icon} {c_disp}</span>
                    <div class="candidate-row-bar-bg">
                        <div class="candidate-row-bar-fill" style="width: {c_pct}%;"></div>
                    </div>
                    <span class="candidate-row-pct">{c_pct}%</span>
                </div>
                """
            st.markdown(bars_html, unsafe_allow_html=True)

            # Toxic Chemical Tags
            if "chemical_hazards" in guidance:
                chems = guidance["chemical_hazards"]
                tags = " ".join([f"<span style='background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; color: #e2e8f0; margin-right: 6px;'>🧪 {c}</span>" for c in chems])
                st.markdown(f"<div style='margin: 12px 0 16px 0;'><b>Identified Toxins:</b> {tags}</div>", unsafe_allow_html=True)

            # Safe handling procedures in collapsible
            if "safe_handling" in guidance:
                with st.expander("🛡️ Safe Handling Protocols & Emergency Action", expanded=False):
                    h = guidance["safe_handling"]
                    if "dos" in h:
                        st.markdown("**Recommended Actions (DO):**")
                        for d in h["dos"]:
                            st.markdown(f"- ✅ {d}")
                    if "donts" in h:
                        st.markdown("**Prohibited Actions (DON'T):**")
                        for dt in h["donts"]:
                            st.markdown(f"- ❌ {dt}")
                    if "emergency" in h:
                        st.warning(f"🚨 **Emergency Action:** {h['emergency']}")

            # Direct action buttons
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("📍 Find Bengaluru Recyclers", type="primary", use_container_width=True):
                    st.session_state["filter_category"] = pred
                    # Switch to recyclers directory page
                    st.switch_page("frontend/views/recyclers.py") if hasattr(st, "switch_page") else None
            with col_b2:
                if st.button("🔄 Scan Another Item", type="secondary", use_container_width=True):
                    st.session_state["active_image_bytes"] = None
                    st.session_state["current_scan_result"] = None
                    st.rerun()

            st.caption(
                f"⚡ Latency: Preprocess `{latency['preprocess']} ms` | Forward Pass `{latency['inference']} ms` | Total `{latency['total']} ms`"
            )
