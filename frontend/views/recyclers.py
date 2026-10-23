"""
frontend/views/recyclers.py
───────────────────────────
Dedicated Bengaluru Recycling Facilities Locator.
Features interactive map, GPS proximity calculation via Haversine formula,
and direct facility contact information verified under KSPCB.
"""

import streamlit as st
import pandas as pd
from backend.geo_service import get_nearest_centers
from src.utils.class_loader import get_class_names

BLR_PRESETS = {
    "Central Bengaluru (Vidhana Soudha / Majestic)": (12.9716, 77.5946),
    "Electronic City (Phase 1 & 2)": (12.8452, 77.6602),
    "Whitefield / ITPL": (12.9850, 77.7315),
    "Koramangala": (12.9352, 77.6245),
    "Indiranagar / Old Airport Road": (12.9784, 77.6408),
    "Peenya Industrial Area": (13.0285, 77.5197),
    "Yelahanka / North Bengaluru": (13.1007, 77.5963),
    "Custom GPS Coordinates": None,
}


def render_recyclers_page():
    """Renders the Bengaluru E-Waste Recycling Directory and Proximity Locator."""
    st.markdown(
        """
        <div class="app-header">
            <h1>📍 Bengaluru Recycler Locator</h1>
            <p>Locate certified KSPCB & CPCB authorized electronic waste dismantlers across Karnataka.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter toolbar
    col_loc, col_mat, col_limit = st.columns([1.5, 1.2, 0.8], gap="medium")

    with col_loc:
        selected_location = st.selectbox(
            "Your Location in Bengaluru:",
            list(BLR_PRESETS.keys()),
            index=0,
        )
        if selected_location == "Custom GPS Coordinates":
            c_lat = st.number_input("Latitude", value=12.9716, format="%.4f")
            c_lon = st.number_input("Longitude", value=77.5946, format="%.4f")
        else:
            coords = BLR_PRESETS[selected_location]
            c_lat, c_lon = coords[0], coords[1]

    with col_mat:
        classes = ["All Categories"] + get_class_names()
        prefill_cat = st.session_state.get("filter_category", "All Categories")
        def_idx = classes.index(prefill_cat) if prefill_cat in classes else 0
        selected_mat = st.selectbox(
            "Filter Material Accepted:",
            classes,
            index=def_idx,
        )

    with col_limit:
        limit = st.selectbox("Show Nearest:", [3, 5, 8], index=1)

    mat_filter = None if selected_mat == "All Categories" else selected_mat
    results = get_nearest_centers(
        user_lat=c_lat,
        user_lon=c_lon,
        class_name=mat_filter,
        limit=limit,
    )

    st.markdown("---")

    # Map & Facilities Layout
    col_map, col_cards = st.columns([1.1, 1], gap="large")

    with col_map:
        st.markdown(f"### Interactive Map ({len(results)} Facilities)")
        map_points = [
            {"lat": c_lat, "lon": c_lon, "name": f"📍 You ({selected_location})"}
        ]
        for idx, r in enumerate(results, 1):
            map_points.append({
                "lat": r["coordinates"]["lat"],
                "lon": r["coordinates"]["lon"],
                "name": f"#{idx} {r['name']} ({r['distance_km']} km)",
            })

        df_map = pd.DataFrame(map_points)
        st.map(df_map, latitude="lat", longitude="lon", zoom=11)
        st.caption("Center point: Your selected location | Pins: KSPCB licensed recyclers")

    with col_cards:
        st.markdown(f"### Nearest Facilities")

        if not results:
            st.warning("No facilities found accepting this specific category.")
        else:
            for idx, r in enumerate(results, 1):
                tags = " ".join([f"<span style='background: rgba(255,255,255,0.06); color: #cbd5e1; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-right: 4px;'>{cat}</span>" for cat in r["categories_accepted"]])
                st.markdown(
                    f"""
                    <div class="recycler-card-dark">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                            <h4 style="margin: 0; color: #ffffff; font-size: 1.05rem; font-weight: 700;">#{idx} {r['name']}</h4>
                            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; font-size: 0.85rem; padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(16, 185, 129, 0.3);">
                                {r['distance_km']} km
                            </span>
                        </div>
                        <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #cbd5e1;"><b>📍 Address:</b> {r['address']}</p>
                        <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #cbd5e1;">
                            <b>📞 Phone:</b> <a href="tel:{r['phone']}" style="color: #10b981; text-decoration: none; font-weight: 600;">{r['phone']}</a> |
                            <b>✉️ Email:</b> <a href="mailto:{r['email']}" style="color: #10b981; text-decoration: none;">{r['email']}</a>
                        </p>
                        <p style="margin: 0 0 8px 0; font-size: 0.8rem; color: #94a3b8;">
                            <b>Authorization:</b> <code>{r.get('kspcb_auth_no', 'KSPCB/CPCB Registered')}</code>
                        </p>
                        <div style="margin-top: 6px;">
                            <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 600; margin-right: 6px;">Accepted:</span>
                            {tags}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
