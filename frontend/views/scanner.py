"""
frontend/views/scanner.py
─────────────────────────
Modern Dark SaaS (Linear / Vercel aesthetic) E-Waste Classifier.
Features:
  - Custom drag-and-drop zone & Camera HUD with AI Vision reticles.
  - One-click sample test presets (Battery, Phone, PCB, CFL Bulb).
  - SVG Circular Confidence Ring Gauge.
  - In-page collapsible Scanner Settings (Cutoff & Focus Mode).
  - Two equal columns, minimal clutter, crisp typography.
  - Direct navigation to Recyclers Directory.
"""

import io
from pathlib import Path
from PIL import Image
import streamlit as st

from config import DEFAULT_CONFIDENCE_THRESHOLD
from backend.inference import get_inference_engine
from frontend.utils.history import record_scan
from frontend.components.badges import render_hazard_badge, render_privacy_pill
from frontend.components.cards import render_candidate_row

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "processed" / "test"

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


def _render_confidence_ring(confidence: float, is_confident: bool) -> str:
    """Renders a sleek SVG circular progress ring gauge."""
    pct = round(confidence * 100, 1)
    stroke_color = "#10b981" if is_confident else "#f59e0b"
    # Circumference for r=36 is 2 * pi * 36 ≈ 226.19
    offset = 226.19 * (1.0 - min(1.0, max(0.0, confidence)))
    return f"""
    <div style="position: relative; width: 88px; height: 88px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <svg width="88" height="88" viewBox="0 0 88 88" style="transform: rotate(-90deg);">
            <circle cx="44" cy="44" r="36" stroke="rgba(255,255,255,0.08)" stroke-width="6" fill="transparent" />
            <circle cx="44" cy="44" r="36" stroke="{stroke_color}" stroke-width="6" fill="transparent"
                    stroke-dasharray="226.19" stroke-dashoffset="{offset:.2f}" stroke-linecap="round" />
        </svg>
        <div style="position: absolute; text-align: center;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #ffffff; line-height: 1;">{pct}%</div>
            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;">MATCH</div>
        </div>
    </div>
    """


def _load_sample_bytes(category: str) -> bytes | None:
    """Loads a real verified test image from data/processed/test/ for one-click testing."""
    cat_dir = SAMPLES_DIR / category
    if cat_dir.exists():
        files = list(cat_dir.glob("*.jpg")) + list(cat_dir.glob("*.jpeg")) + list(cat_dir.glob("*.png"))
        if files:
            return files[0].read_bytes()
    return None


def render_scanner_page():
    """Renders the Modern SaaS E-Waste Neural Scanner view."""
    # 1. Linear Header Bar
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1>📸 E-Waste Vision Terminal</h1>
                <p>Quantized INT8 edge classifier & statutory hazard assessment under India E-Waste Rules 2022.</p>
            </div>
            <span class="privacy-pill">🔒 Volatile RAM Only • Zero Disk Storage</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. In-Page Collapsible Settings
    with st.expander("⚙️ Vision Engine Configuration (Sensitivity & Focus Mode)", expanded=False):
        c_set1, c_set2 = st.columns(2, gap="medium")
        with c_set1:
            threshold = st.slider(
                "Confidence Cutoff Threshold:",
                min_value=0.50,
                max_value=0.90,
                value=float(DEFAULT_CONFIDENCE_THRESHOLD),
                step=0.05,
                help="Classifications with confidence below this threshold trigger precautionary retake guidance.",
                key="scanner_threshold",
            )
            st.caption(f"Statutory calibrated threshold: **{threshold:.2f}**")
        with c_set2:
            smart_crop = st.toggle(
                "Subject Focus Mode (Auto 67% Center-Crop)",
                value=False,
                help="Auto-crops the central 67% to strip out background table surfaces and specular glare.",
                key="scanner_smart_crop",
            )
            center_crop_fraction = 0.67 if smart_crop else 1.0
            if smart_crop:
                st.success("✅ Focus active: 67% central zone isolated")
            else:
                st.caption("Recommended for real-world phone shots on wide tables.")

    # Initialize Session State
    if "active_image_bytes" not in st.session_state:
        st.session_state["active_image_bytes"] = None
    if "current_scan_result" not in st.session_state:
        st.session_state["current_scan_result"] = None

    # 3. Two-Column SaaS Layout
    col_upload, col_analysis = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("### 1. Visual Input")

        # Tabbed Input: Upload / Camera / Quick Presets
        input_tab_upload, input_tab_camera, input_tab_presets = st.tabs([
            "📁 File Dropzone",
            "📷 Camera HUD",
            "⚡ Quick Presets",
        ])

        loaded_bytes = st.session_state.get("active_image_bytes")
        preview_pil = None
        if loaded_bytes:
            try:
                preview_pil = Image.open(io.BytesIO(loaded_bytes))
            except Exception:
                preview_pil = None

        with input_tab_upload:
            st.markdown(
                """
                <div class="modern-dropzone">
                    <div style="font-size: 1.6rem; margin-bottom: 4px;">☁️</div>
                    <div style="font-weight: 600; font-size: 0.9rem; color: #ffffff;">Drop E-Waste Photo Here</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">Accepts JPG, PNG, WebP up to 10 MB</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            up_file = st.file_uploader(
                "Upload Photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="modern_file_uploader",
                label_visibility="collapsed",
            )
            if up_file is not None:
                new_bytes = up_file.getvalue()
                if new_bytes != loaded_bytes:
                    loaded_bytes = new_bytes
                    st.session_state["active_image_bytes"] = loaded_bytes
                    st.session_state["current_scan_result"] = None
                    preview_pil = Image.open(io.BytesIO(loaded_bytes))
                    st.rerun()

        with input_tab_camera:
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;'>Point camera at e-waste item and capture:</div>", unsafe_allow_html=True)
            cam_file = st.camera_input("Capture with device camera", key="modern_camera_input", label_visibility="collapsed")
            if cam_file is not None:
                new_bytes = cam_file.getvalue()
                if new_bytes != loaded_bytes:
                    loaded_bytes = new_bytes
                    st.session_state["active_image_bytes"] = loaded_bytes
                    st.session_state["current_scan_result"] = None
                    preview_pil = Image.open(io.BytesIO(loaded_bytes))
                    st.rerun()

        with input_tab_presets:
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;'>Instant test samples from test split:</div>", unsafe_allow_html=True)
            p_c1, p_c2 = st.columns(2, gap="small")
            with p_c1:
                if st.button("🔋 Sample Battery", use_container_width=True, type="secondary", key="sample_battery"):
                    b = _load_sample_bytes("battery")
                    if b:
                        st.session_state["active_image_bytes"] = b
                        st.session_state["current_scan_result"] = None
                        st.rerun()
                if st.button("🔌 Sample PCB", use_container_width=True, type="secondary", key="sample_pcb"):
                    b = _load_sample_bytes("pcb")
                    if b:
                        st.session_state["active_image_bytes"] = b
                        st.session_state["current_scan_result"] = None
                        st.rerun()
            with p_c2:
                if st.button("📱 Sample Phone", use_container_width=True, type="secondary", key="sample_phone"):
                    b = _load_sample_bytes("mobile_phone")
                    if b:
                        st.session_state["active_image_bytes"] = b
                        st.session_state["current_scan_result"] = None
                        st.rerun()
                if st.button("💡 Sample CFL Bulb", use_container_width=True, type="secondary", key="sample_cfl"):
                    b = _load_sample_bytes("cfl_bulb")
                    if b:
                        st.session_state["active_image_bytes"] = b
                        st.session_state["current_scan_result"] = None
                        st.rerun()

        # Camera HUD Viewfinder (when an image is loaded)
        if preview_pil is not None:
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

            zoom_val = st.select_slider(
                "🔍 Framing Focus & Zoom:",
                options=[1.0, 1.2, 1.3, 1.5],
                value=1.0,
                format_func=lambda z: f"{z}x Close-up" if z > 1.0 else "1.0x Full Frame",
                key="scanner_zoom_slider",
            )

            processed_bytes = loaded_bytes
            if zoom_val > 1.0:
                w, h = preview_pil.size
                cw, ch = int(w / zoom_val), int(h / zoom_val)
                left, top = (w - cw) // 2, (h - ch) // 2
                preview_pil = preview_pil.crop((left, top, left + cw, top + ch))
                buf = io.BytesIO()
                preview_pil.save(buf, format="JPEG")
                processed_bytes = buf.getvalue()

            # Render HUD Viewfinder with Targeting Brackets
            st.markdown(
                f"""
                <div class="hud-viewfinder">
                    <div class="hud-reticle-tl"></div>
                    <div class="hud-reticle-tr"></div>
                    <div class="hud-reticle-bl"></div>
                    <div class="hud-reticle-br"></div>
                    <div class="hud-center-crosshair"></div>
                    <div class="hud-overlay">
                        <div class="hud-top-bar">
                            <span class="hud-telemetry">● LIVE VISION HUD</span>
                            <span class="hud-telemetry">{zoom_val}X OPTICAL FOCUS</span>
                        </div>
                        <div class="hud-bottom-bar">
                            <span class="hud-telemetry">INT8 QUANT • 224x224</span>
                            <span class="hud-telemetry">STATE: TARGET ACQUIRED</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.image(preview_pil, use_container_width=True)

            # Prominent Action CTA
            analyze_clicked = st.button(
                "⚡ Analyze & Classify E-Waste",
                type="primary",
                use_container_width=True,
                key="btn_run_classify",
            )

            if analyze_clicked:
                with st.spinner("Executing INT8 ONNX Forward Pass & Temperature Scaling..."):
                    try:
                        engine = get_inference_engine()
                        res = engine.predict(
                            image_bytes=processed_bytes,
                            threshold=threshold,
                            center_crop_fraction=center_crop_fraction,
                        )
                        st.session_state["current_scan_result"] = res

                        # Record scan metadata
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
                        st.error(f"Inference failure: {str(e)}")

    with col_analysis:
        st.markdown("### 2. Telemetry & Results")

        res = st.session_state.get("current_scan_result")

        # State A: Empty State
        if res is None:
            if preview_pil is None:
                st.markdown(
                    """
                    <div class="dark-card" style="text-align: center; padding: 64px 20px;">
                        <div style="font-size: 2.8rem; margin-bottom: 10px; opacity: 0.6;">🎯</div>
                        <h4 style="color: #ffffff; margin-bottom: 4px; font-weight: 600;">Awaiting Visual Input</h4>
                        <p style="font-size: 0.85rem; color: #94a3b8; margin: 0; max-width: 320px; margin: 0 auto;">
                            Drop an e-waste image or pick a preset sample on the left to begin classification.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="dark-card" style="text-align: center; padding: 54px 20px; border-color: rgba(16, 185, 129, 0.4) !important;">
                        <div style="font-size: 2.6rem; margin-bottom: 8px;">⚡</div>
                        <h4 style="color: #ffffff; margin-bottom: 4px; font-weight: 700;">Target Frame Locked</h4>
                        <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;">
                            Click <b>Analyze & Classify E-Waste</b> to evaluate hazard and recycling protocols.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            # State B: Hero HUD Result Card
            pred = res["prediction"]
            conf = res["calibrated_confidence"]
            is_conf = res["is_confident"]
            guidance = res["guidance"]
            top_3 = res["top_3"]
            latency = res.get("latency_ms", {})

            icon = CLASS_ICONS.get(pred, "📦")
            display_name = CLASS_DISPLAY.get(pred, pred.replace("_", " ").title())
            hazard_level = guidance.get("hazard_level", "MODERATE").upper()

            # Hero Card with SVG Radial Confidence Gauge
            ring_html = _render_confidence_ring(conf, is_conf)
            badge_html = render_hazard_badge(hazard_level)

            st.markdown(
                f"""
                <div class="dark-card" style="border-color: rgba(16, 185, 129, 0.3) !important; padding: 20px !important;">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <span style="font-size: 2.6rem; line-height: 1;">{icon}</span>
                            <div>
                                <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; font-weight: 600;">Identified E-Waste</div>
                                <h2 style="margin: 2px 0 6px 0; font-size: 1.35rem; color: #ffffff; font-weight: 800; letter-spacing: -0.02em;">{display_name}</h2>
                                {badge_html}
                            </div>
                        </div>
                        {ring_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Safeguard Warning if uncertain
            if not is_conf or guidance.get("status") == "uncertain":
                st.warning(
                    f"⚠️ **Precautionary Safeguard Active:** Match confidence is below statutory cutoff ({threshold*100:.0f}%). "
                    "If photo is blurred or reflective, toggle Subject Focus Mode or zoom 1.2x."
                )

            # Top 3 Candidates
            st.markdown("##### Candidate Distribution")
            for item in top_3:
                c_name = item["label"]
                c_icon = CLASS_ICONS.get(c_name, "📦")
                c_disp = CLASS_DISPLAY.get(c_name, c_name.replace("_", " ").title())
                st.markdown(
                    render_candidate_row(c_disp, item["confidence"], c_icon),
                    unsafe_allow_html=True,
                )

            # Materials / Chemical Toxins
            if "chemical_hazards" in guidance:
                chems = guidance["chemical_hazards"]
                tags = " ".join([
                    f"<span style='background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); "
                    f"padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; color: #cbd5e1; margin-right: 4px;'>"
                    f"🧪 {c}</span>"
                    for c in chems
                ])
                st.markdown(f"<div style='margin: 12px 0 14px 0;'><b>Identified Toxins:</b> {tags}</div>", unsafe_allow_html=True)

            # Handling Protocols Checklist (Linear Clean Style)
            if "safe_handling" in guidance:
                with st.expander("🛡️ Safe Handling & Disposal Checklist", expanded=True):
                    h = guidance["safe_handling"]
                    if "dos" in h:
                        st.markdown("**Recommended DOs:**")
                        for d in h["dos"]:
                            st.markdown(f"- ✅ {d}")
                    if "donts" in h:
                        st.markdown("**Prohibited DONTs:**")
                        for dt in h["donts"]:
                            st.markdown(f"- ❌ {dt}")
                    if "emergency" in h:
                        st.error(f"🚨 **Emergency Action:** {h['emergency']}")

            # Direct Navigation Actions
            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2, gap="medium")
            with col_b1:
                if st.button("📍 Find Nearest Recycler", type="primary", use_container_width=True, key="btn_go_recyclers"):
                    st.session_state["filter_category"] = pred
                    if "page_recyclers" in st.session_state and hasattr(st, "switch_page"):
                        st.switch_page(st.session_state["page_recyclers"])
                    else:
                        st.info("Filter applied! Open 'Recyclers Directory' in the sidebar.")
            with col_b2:
                if st.button("🔄 Scan Another Item", type="secondary", use_container_width=True, key="btn_reset_scan"):
                    st.session_state["active_image_bytes"] = None
                    st.session_state["current_scan_result"] = None
                    st.rerun()

            if latency:
                st.caption(
                    f"⚡ Latency: Preprocess `{latency.get('preprocess', 0)} ms` | "
                    f"INT8 Forward `{latency.get('inference', 0)} ms` | "
                    f"Total `{latency.get('total', 0)} ms`"
                )
