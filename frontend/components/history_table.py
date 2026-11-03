"""
frontend/components/history_table.py
────────────────────────────────────
Interactive, high-contrast history list with filtering, pagination,
details dialog, CSV export, single record deletion, and clear-all confirmation.
"""

import math
from datetime import datetime, date
import streamlit as st
import pandas as pd

from frontend.utils.history import (
    get_user_history_filtered,
    count_user_history_filtered,
    delete_scan,
    clear_user_history,
    export_user_history_csv,
    get_user_stats,
)
from frontend.components.badges import render_hazard_badge

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
    "cfl_bulb": "CFL / Mercury Lamp",
    "keyboard": "Keyboard / Peripheral",
    "mobile_phone": "Smartphone / Phone",
    "monitor_crt": "Cathode Ray Tube (CRT)",
    "pcb": "Circuit Board (PCB)",
    "other": "Unclassified E-Waste",
}

# Dialog for detailed inspection of a single scan
if hasattr(st, "dialog"):
    @st.dialog("🔍 E-Waste Audit Details")
    def _render_details_modal(scan: dict):
        pred = scan["prediction"]
        conf = scan["confidence"]
        hazard = scan["hazard_level"]
        timestamp = scan["scanned_at"]
        icon = CLASS_ICONS.get(pred, "📦")
        display_name = CLASS_DISPLAY.get(pred, pred.replace("_", " ").title())

        st.markdown(
            f"""
            <div style="background: #11131a; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 2rem;">{icon}</span>
                        <div>
                            <h3 style="margin: 0; color: #ffffff; font-size: 1.2rem;">{display_name}</h3>
                            <span style="font-size: 0.8rem; color: #94a3b8;">Recorded: {timestamp}</span>
                        </div>
                    </div>
                    {render_hazard_badge(hazard)}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem; color: #cbd5e1; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 12px;">
                    <div><b>Audit Record ID:</b> #{scan['id']}</div>
                    <div><b>Model Confidence:</b> <span style="color: #10b981; font-weight: 700;">{conf * 100:.2f}%</span></div>
                    <div><b>Storage Protocol:</b> In-Memory Protected</div>
                    <div><b>Raw Image Stored:</b> <span style="color: #34d399;">NO (Zero Disk Leak)</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info("🔒 **Privacy Guarantee:** In accordance with our security principles, only classification metadata is archived. Raw image bytes were erased from volatile RAM immediately following inference.")

        if st.button("Close", type="secondary", use_container_width=True, key=f"close_modal_{scan['id']}"):
            st.rerun()

    @st.dialog("⚠️ Confirm Complete History Purge")
    def _render_clear_all_modal(username: str):
        st.warning("Are you sure you want to permanently clear your entire e-waste scan history? This action cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Clear History", type="primary", use_container_width=True):
                clear_user_history(username)
                st.session_state["history_page"] = 1
                st.success("All scan history records have been erased.")
                st.rerun()
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                st.rerun()


def render_history_component(username: str, on_navigate_scanner=None):
    """
    Renders the full Account & History view with profile stats, summary metrics,
    filters, card list/table, pagination, CSV download, and deletion controls.
    """
    # 1. Summary Metrics Row
    stats = get_user_stats(username)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4, gap="medium")
    with m_col1:
        st.metric("Total Scans Evaluated", stats["total_scans"])
    with m_col2:
        st.metric("Hazardous Items Flagged", stats["hazardous_items"], delta=None)
    with m_col3:
        st.metric("Recyclable Materials", stats["recyclable_items"])
    with m_col4:
        st.metric("Top E-Waste Category", stats["top_category"])

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # 2. Filter Toolbar
    with st.expander("🔍 Filter & Search Audit History", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.2, 1.2, 1.4], gap="medium")

        with f_col1:
            cat_options = ["All", "battery", "cfl_bulb", "keyboard", "mobile_phone", "monitor_crt", "pcb", "other"]
            sel_cat = st.selectbox(
                "Filter Category:",
                cat_options,
                format_func=lambda x: "All Categories" if x == "All" else CLASS_DISPLAY.get(x, x),
                key="hist_filter_cat",
            )

        with f_col2:
            hazard_options = ["All", "LOW", "MODERATE", "HIGH", "CRITICAL"]
            sel_hazard = st.selectbox(
                "Filter Hazard Level:",
                hazard_options,
                format_func=lambda x: "All Levels" if x == "All" else f"{x} HAZARD",
                key="hist_filter_hazard",
            )

        with f_col3:
            date_filter = st.date_input(
                "Date Range:",
                value=[],
                key="hist_date_range",
                help="Select start and end dates to filter scans.",
            )

        with f_col4:
            search_query = st.text_input(
                "Search History:",
                placeholder="Search material or hazard...",
                key="hist_search_box",
            )

    # Extract date range
    date_from = None
    date_to = None
    if isinstance(date_filter, (list, tuple)):
        if len(date_filter) >= 1:
            date_from = date_filter[0].strftime("%Y-%m-%d")
        if len(date_filter) >= 2:
            date_to = date_filter[1].strftime("%Y-%m-%d")
    elif isinstance(date_filter, date):
        date_from = date_filter.strftime("%Y-%m-%d")

    # Pagination state
    if "history_page" not in st.session_state:
        st.session_state["history_page"] = 1

    page_size = 10
    total_records = count_user_history_filtered(
        username=username,
        category=sel_cat,
        hazard_level=sel_hazard,
        date_from=date_from,
        date_to=date_to,
        search_query=search_query,
    )
    total_pages = max(1, math.ceil(total_records / page_size))

    if st.session_state["history_page"] > total_pages:
        st.session_state["history_page"] = 1

    current_page = st.session_state["history_page"]
    offset = (current_page - 1) * page_size

    # Fetch records
    records = get_user_history_filtered(
        username=username,
        category=sel_cat,
        hazard_level=sel_hazard,
        date_from=date_from,
        date_to=date_to,
        search_query=search_query,
        limit=page_size,
        offset=offset,
    )

    # Action Toolbar: Export CSV & Clear All
    act_col1, act_col2, act_col3 = st.columns([1.5, 1, 1], gap="medium")
    with act_col1:
        st.caption(f"Showing **{len(records)}** of **{total_records}** total records (Page {current_page} of {total_pages})")
    with act_col2:
        csv_data = export_user_history_csv(username)
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name=f"ecoscan_history_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_export_csv",
        )
    with act_col3:
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True, key="btn_clear_all"):
            if hasattr(st, "dialog"):
                _render_clear_all_modal(username)
            else:
                clear_user_history(username)
                st.rerun()

    st.markdown("---")

    # Empty State Handling
    if not records:
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 48px 24px;">
                <div style="font-size: 3rem; margin-bottom: 12px;">📭</div>
                <h3 style="color: #ffffff; margin-bottom: 8px;">No Scan Records Found</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto 20px auto;">
                    You haven't scanned any electronic items matching the current filter, or your history is empty.
                    Test the AI neural classifier on an e-waste photo!
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if on_navigate_scanner:
            col_cen1, col_cen2, col_cen3 = st.columns([1, 1, 1])
            with col_cen2:
                if st.button("📸 Go to Scanner & Classifier", type="primary", use_container_width=True):
                    on_navigate_scanner()
        return

    # 3. Card List View
    for r in records:
        scan_id = r["id"]
        pred = r["prediction"]
        conf = r["confidence"]
        hazard = r["hazard_level"]
        timestamp = str(r["scanned_at"])[:19]
        icon = CLASS_ICONS.get(pred, "📦")
        display_name = CLASS_DISPLAY.get(pred, pred.replace("_", " ").title())

        with st.container():
            c_icon, c_info, c_badge, c_btns = st.columns([0.6, 2.2, 1.2, 1.4], gap="small")

            with c_icon:
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
                                border-radius: 10px; width: 44px; height: 44px; display: flex;
                                align-items: center; justify-content: center; font-size: 1.5rem; margin-top: 4px;">
                        {icon}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_info:
                st.markdown(
                    f"""
                    <div style="margin-top: 2px;">
                        <span style="font-weight: 700; font-size: 1rem; color: #ffffff;">{display_name}</span>
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 2px;">
                            📅 {timestamp} • Confidence: <b style="color: #10b981;">{conf * 100:.1f}%</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_badge:
                st.markdown(
                    f"<div style='margin-top: 8px;'>{render_hazard_badge(hazard)}</div>",
                    unsafe_allow_html=True,
                )

            with c_btns:
                b_col1, b_col2 = st.columns(2, gap="small")
                with b_col1:
                    if st.button("Details", key=f"view_det_{scan_id}", use_container_width=True, type="secondary"):
                        if hasattr(st, "dialog"):
                            _render_details_modal(r)
                        else:
                            st.session_state[f"exp_det_{scan_id}"] = not st.session_state.get(f"exp_det_{scan_id}", False)
                with b_col2:
                    if st.button("🗑️", key=f"del_scan_{scan_id}", use_container_width=True, help="Delete this scan record"):
                        delete_scan(scan_id, username)
                        st.rerun()

            # Fallback expander if st.dialog is not used
            if not hasattr(st, "dialog") and st.session_state.get(f"exp_det_{scan_id}", False):
                with st.expander(f"Audit Metadata #{scan_id}", expanded=True):
                    st.write(r)

            st.markdown("<div style='border-bottom: 1px solid rgba(255,255,255,0.04); margin: 6px 0 10px 0;'></div>", unsafe_allow_html=True)

    # 4. Pagination Controls
    if total_pages > 1:
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        p_col1, p_col2, p_col3 = st.columns([1, 2, 1])

        with p_col1:
            if current_page > 1:
                if st.button("⬅️ Previous", key="btn_prev_page", use_container_width=True):
                    st.session_state["history_page"] = current_page - 1
                    st.rerun()

        with p_col2:
            st.markdown(
                f"<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding-top: 6px;'>"
                f"Page <b>{current_page}</b> of <b>{total_pages}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with p_col3:
            if current_page < total_pages:
                if st.button("Next ➡️", key="btn_next_page", use_container_width=True):
                    st.session_state["history_page"] = current_page + 1
                    st.rerun()
