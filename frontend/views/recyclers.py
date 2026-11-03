"""
frontend/views/recyclers.py
───────────────────────────
Searchable directory and map of certified KSPCB & CPCB e-waste recyclers.
Allows filtering by city / Bengaluru cluster and accepted material type.
Includes detailed operating hours, directions, and step-by-step disposal procedures.
"""

import datetime
import streamlit as st
import pandas as pd

from backend.geo_service import get_nearest_centers, load_recyclers_db
from src.utils.class_loader import get_class_names
from frontend.components.badges import render_status_badge

# Location presets across Bengaluru & Karnataka
BLR_PRESETS = {
    "Central Bengaluru (Vidhana Soudha / Majestic)": (12.9716, 77.5946),
    "Electronic City (Phase 1 & 2)":                 (12.8452, 77.6602),
    "Whitefield / ITPL":                              (12.9850, 77.7315),
    "Koramangala / BTM":                              (12.9352, 77.6245),
    "Indiranagar / Old Airport Road":                 (12.9784, 77.6408),
    "Peenya Industrial Area":                         (13.0285, 77.5197),
    "Yelahanka / North Bengaluru":                    (13.1007, 77.5963),
    "Nelamangala / Dobbspet Industrial Corridor":     (13.2505, 77.2415),
    "Custom GPS Coordinates":                         None,
}

CLASS_ICONS = {
    "battery":      "🔋",
    "cfl_bulb":     "💡",
    "keyboard":     "⌨️",
    "mobile_phone": "📱",
    "monitor_crt":  "🖥️",
    "pcb":          "🔌",
    "other":        "📦",
}

CLASS_DISPLAY = {
    "battery":      "Battery",
    "cfl_bulb":     "CFL / Mercury Bulb",
    "keyboard":     "Keyboard",
    "mobile_phone": "Mobile Phone",
    "monitor_crt":  "CRT Monitor",
    "pcb":          "Circuit Board (PCB)",
    "other":        "Other E-Waste",
}

DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TODAY = datetime.datetime.now().strftime("%A").lower()


def _is_open_now(hours: dict) -> tuple[bool, str]:
    today_hours = hours.get(TODAY, "Unknown")
    if today_hours in ("Closed", "Unknown"):
        return False, today_hours
    return True, today_hours


def _hours_table_html(hours: dict) -> str:
    rows = ""
    for day_key, label in zip(DAY_ORDER, DAY_LABELS):
        h = hours.get(day_key, "—")
        is_today = (day_key == TODAY)
        closed = (h == "Closed")
        row_bg = "rgba(16,185,129,0.12)" if is_today else "transparent"
        txt_col = "#34d399" if is_today else ("#64748b" if closed else "#e2e8f0")
        day_bold = "font-weight:700;" if is_today else ""
        rows += (
            f"<tr style='background:{row_bg};'>"
            f"<td style='padding:4px 10px;color:{txt_col};{day_bold}'>{label}{'  ← today' if is_today else ''}</td>"
            f"<td style='padding:4px 10px;color:{txt_col};text-align:right;'>{h}</td>"
            f"</tr>"
        )
    return (
        "<table style='width:100%;border-collapse:collapse;font-size:0.82rem;'>"
        + rows
        + "</table>"
    )


def _disposal_steps_html(steps: list) -> str:
    items = "".join(
        f"<li style='margin-bottom:6px;color:#cbd5e1;font-size:0.85rem;'>{s}</li>"
        for s in steps
    )
    return f"<ol style='padding-left:18px;margin:0;'>{items}</ol>"


def render_recyclers_page():
    """Renders the Bengaluru E-Waste Recycling Directory and Proximity Locator."""
    st.markdown(
        """
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>📍 Recyclers Directory & Locator</h1>
                    <p>Search KSPCB & CPCB certified electronic waste dismantlers across Bengaluru and Karnataka.</p>
                </div>
                <span class="privacy-pill">🏛️ KSPCB / CPCB Certified</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter Toolbar
    col_loc, col_mat, col_limit = st.columns([1.5, 1.2, 0.8], gap="medium")

    with col_loc:
        selected_location = st.selectbox(
            "Your Location / Cluster:",
            list(BLR_PRESETS.keys()),
            index=0,
            key="recycler_loc_select",
        )
        if selected_location == "Custom GPS Coordinates":
            c_lat = st.number_input("Latitude", value=12.9716, format="%.4f", key="rec_lat")
            c_lon = st.number_input("Longitude", value=77.5946, format="%.4f", key="rec_lon")
        else:
            coords = BLR_PRESETS[selected_location]
            c_lat, c_lon = coords

    with col_mat:
        classes = ["All Categories"] + get_class_names()
        prefill_cat = st.session_state.get("filter_category", "All Categories")
        def_idx = classes.index(prefill_cat) if prefill_cat in classes else 0
        selected_mat = st.selectbox(
            "Filter Material Accepted:",
            classes,
            index=def_idx,
            format_func=lambda x: "All Categories" if x == "All Categories" else f"{CLASS_ICONS.get(x, '')} {CLASS_DISPLAY.get(x, x)}",
            key="recycler_mat_select",
        )

    with col_limit:
        limit = st.selectbox("Show Nearest:", [3, 5, 8], index=1, key="recycler_limit_select")

    mat_filter = None if selected_mat == "All Categories" else selected_mat
    results = get_nearest_centers(user_lat=c_lat, user_lon=c_lon, class_name=mat_filter, limit=limit)

    # Load full JSON for hours, disposal steps, and URLs
    db_data = load_recyclers_db()
    full_db = {c["id"]: c for c in db_data.get("centers", [])}

    st.markdown("---")

    # Map & Facilities Layout
    col_map, col_cards = st.columns([1.1, 1], gap="large")

    with col_map:
        st.markdown(f"### 🗺️ Facility Map ({len(results)} Located)")
        map_points = [{"lat": c_lat, "lon": c_lon, "name": f"📍 You ({selected_location})"}]
        for idx, r in enumerate(results, 1):
            map_points.append({
                "lat": r["coordinates"]["lat"],
                "lon": r["coordinates"]["lon"],
                "name": f"#{idx} {r['name']} ({r['distance_km']} km)",
            })
        df_map = pd.DataFrame(map_points)
        st.map(df_map, latitude="lat", longitude="lon", zoom=11)
        st.caption("Center point: Your chosen location | Blue pins: KSPCB licensed facilities")

    with col_cards:
        st.markdown("### 🏭 Nearest Facilities")
        st.caption("Click **▶ View Full Details** on any facility for hours, directions, and material guidance.")

        if not results:
            st.warning("No facilities found accepting this specific category. Try 'All Categories'.")
        else:
            for idx, r in enumerate(results, 1):
                rich = full_db.get(r["id"], r)
                hours = rich.get("opening_hours", {})
                is_open, today_h = _is_open_now(hours)

                status_html = render_status_badge(is_open, today_h)

                tags_html = " ".join([
                    f"<span style='background:rgba(255,255,255,0.06);color:#94a3b8;padding:2px 7px;border-radius:4px;font-size:0.72rem;margin-right:3px;'>"
                    f"{CLASS_ICONS.get(cat, '📦')} {CLASS_DISPLAY.get(cat, cat)}</span>"
                    for cat in r["categories_accepted"]
                ])

                st.markdown(
                    f"""
                    <div class="recycler-card-dark">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span style="background:#10b981;color:#000;font-weight:800;font-size:0.85rem;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                                    {idx}
                                </span>
                                <div>
                                    <div style="font-weight:700;font-size:0.95rem;color:#ffffff;">{r['name']}</div>
                                    <div style="font-size:0.75rem;color:#94a3b8;margin-top:1px;">📌 {r.get('cluster', '')}</div>
                                </div>
                            </div>
                            <span style="background:rgba(16,185,129,0.15);color:#34d399;font-weight:800;font-size:0.82rem;padding:3px 10px;border-radius:9999px;border:1px solid rgba(16,185,129,0.3);">
                                {r['distance_km']} km
                            </span>
                        </div>
                        <div style="font-size:0.82rem;color:#cbd5e1;margin-bottom:6px;">📍 {r['address']}</div>
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;">
                            {status_html}
                            <span style="font-size:0.78rem;color:#94a3b8;">Today: <b style="color:#e2e8f0;">{today_h}</b></span>
                        </div>
                        <div style="display:flex;flex-wrap:wrap;gap:4px;">{tags_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"▶ View Full Details — {r['name']}", expanded=False):
                    tab_info, tab_hours, tab_dispose = st.tabs(
                        ["📋 Info & Directions", "🕐 Opening Hours", "♻️ How to Dispose"]
                    )

                    with tab_info:
                        st.markdown(
                            f"""
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
                                <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px;">
                                    <div style="font-size:0.7rem;color:#94a3b8;font-weight:600;text-transform:uppercase;">Phone</div>
                                    <a href="tel:{rich.get('phone', '')}" style="color:#10b981;font-weight:700;font-size:0.9rem;text-decoration:none;">
                                        📞 {rich.get('phone', 'N/A')}
                                    </a>
                                </div>
                                <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px;">
                                    <div style="font-size:0.7rem;color:#94a3b8;font-weight:600;text-transform:uppercase;">Email</div>
                                    <a href="mailto:{rich.get('email', '')}" style="color:#10b981;font-weight:700;font-size:0.9rem;text-decoration:none;word-break:break-all;">
                                        ✉️ {rich.get('email', 'N/A')}
                                    </a>
                                </div>
                            </div>
                            <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px;margin-bottom:10px;">
                                <div style="font-size:0.7rem;color:#94a3b8;font-weight:600;text-transform:uppercase;">KSPCB Authorization</div>
                                <div style="color:#fbbf24;font-size:0.82rem;font-family:monospace;">🏛️ {rich.get('kspcb_auth_no', 'N/A')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        maps_url = rich.get("google_maps_url", f"https://maps.google.com/?q={r['coordinates']['lat']},{r['coordinates']['lon']}")
                        b1, b2 = st.columns(2)
                        with b1:
                            st.link_button("🗺️ Open in Google Maps", maps_url, use_container_width=True)
                        with b2:
                            site = rich.get("website", "")
                            if site:
                                st.link_button("🌐 Visit Website", site, use_container_width=True)
                            else:
                                st.button("🌐 Website N/A", disabled=True, use_container_width=True, key=f"site_na_{r['id']}")

                    with tab_hours:
                        if hours:
                            st.markdown(_hours_table_html(hours), unsafe_allow_html=True)
                        else:
                            st.info("Hours not listed. Please phone facility in advance.")

                    with tab_dispose:
                        disposal = rich.get("disposal_instructions", {})
                        if not disposal:
                            st.info("General instruction: Bring items dry, unburned, and segregated by category.")
                        else:
                            for cat in r["categories_accepted"]:
                                steps = disposal.get(cat)
                                if steps:
                                    st.markdown(f"**{CLASS_ICONS.get(cat, '📦')} {CLASS_DISPLAY.get(cat, cat)}:**")
                                    st.markdown(_disposal_steps_html(steps), unsafe_allow_html=True)
