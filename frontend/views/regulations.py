"""
frontend/views/regulations.py
─────────────────────────────
Comprehensive statutory knowledge base and compliance directory
under Government of India E-Waste (Management) Rules 2022.
"""

import streamlit as st
import pandas as pd


def render_regulations_page():
    """Renders India E-Waste Laws, Statutory Obligations, and Hazard Matrix."""
    st.markdown(
        """
        <div class="hero-banner">
            <h1>⚖️ Statutory Framework & Legal Guidelines</h1>
            <p>Government of India E-Waste (Management) Rules 2022 and Battery Waste Management Rules 2022.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Summary Cards
    col_c1, col_c2, col_c3 = st.columns(3, gap="medium")
    with col_c1:
        st.markdown(
            """
            <div class="modern-card">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">📜</div>
                <h4 style="margin: 0 0 6px 0; color: #0f172a;">E-Waste Rules, 2022</h4>
                <p style="font-size: 0.88rem; color: #475569; margin: 0;">
                    Notified by MoEFCC via GSR 816(E). Covers all electrical & electronic equipment across 106 items.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c2:
        st.markdown(
            """
            <div class="modern-card">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🔋</div>
                <h4 style="margin: 0 0 6px 0; color: #0f172a;">Battery Waste Rules</h4>
                <p style="font-size: 0.88rem; color: #475569; margin: 0;">
                    Notified under GSR 664(E). Mandates 100% recovery of critical elements (Lithium, Cobalt, Nickel, Lead).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c3:
        st.markdown(
            """
            <div class="modern-card">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🚨</div>
                <h4 style="margin: 0 0 6px 0; color: #0f172a;">Section 15 Penalties</h4>
                <p style="font-size: 0.88rem; color: #475569; margin: 0;">
                    Environment (Protection) Act, 1986. Imprisonment up to 5 years, ₹1,00,000 fine for illegal disposal/burning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Statutory Classification & Chemical Hazard Matrix")

    hazard_matrix = [
        {
            "E-Waste Category": "Battery (Li-ion / Lead-Acid)",
            "Hazard Level": "CRITICAL",
            "Target Toxins": "Lithium, Cobalt, Sulfuric Acid, Lead, Cadmium",
            "Key Hazards": "Thermal runaway fire explosion, groundwater acid contamination",
            "Statutory Rule": "Battery Waste Rules 2022"
        },
        {
            "E-Waste Category": "CFL / Fluorescent Lamp",
            "Hazard Level": "HIGH",
            "Target Toxins": "Elemental Mercury vapor, Phosphor dust",
            "Key Hazards": "Severe neurotoxicity upon glass breakage and vapor inhalation",
            "Statutory Rule": "E-Waste Rules Schedule I (ITEW20)"
        },
        {
            "E-Waste Category": "Monitor CRT",
            "Hazard Level": "HIGH",
            "Target Toxins": "Lead oxide funnel glass (1-2 kg), Barium",
            "Key Hazards": "High vacuum implosion hazard; lead poisoning upon landfill leaching",
            "Statutory Rule": "E-Waste Rules Schedule I (ITEW1)"
        },
        {
            "E-Waste Category": "Printed Circuit Board (PCB)",
            "Hazard Level": "HIGH",
            "Target Toxins": "Lead solder, Brominated Flame Retardants (PBDEs), Copper",
            "Key Hazards": "Dioxin release from open burning; persistent bioaccumulative chemicals",
            "Statutory Rule": "E-Waste Rules Schedule I (ITEW2)"
        },
        {
            "E-Waste Category": "Mobile Phone",
            "Hazard Level": "MODERATE",
            "Target Toxins": "Lithium-Cobalt battery, Gold, Tantalum, Arsenic",
            "Key Hazards": "Combustible micro-battery; depletion of strategic rare earth minerals",
            "Statutory Rule": "E-Waste Rules Schedule I (ITEW15)"
        },
        {
            "E-Waste Category": "Keyboard / Peripherals",
            "Hazard Level": "LOW",
            "Target Toxins": "ABS plastics, Polybrominated biphenyls",
            "Key Hazards": "Microplastic generation, persistent halogenated flame retardants",
            "Statutory Rule": "E-Waste Rules Schedule I (ITEW4)"
        },
    ]

    df_matrix = pd.DataFrame(hazard_matrix)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)

    st.markdown("---")

    col_q1, col_q2 = st.columns(2, gap="large")

    with col_q1:
        st.markdown("### 🏢 Extended Producer Responsibility (EPR)")
        st.markdown(
            """
            - Every manufacturer, producer, refurbisher, and dismantler must register on the Central Pollution Control Board (CPCB) EPR Portal.
            - Producers are legally liable to take back and safely dismantle end-of-life electronics according to annual percentage quotas.
            - Consumers and commercial bulk generators must deliver e-waste exclusively to CPCB/KSPCB certified recyclers with traceable manifests.
            """
        )

    with col_q2:
        st.markdown("### 🚫 Prohibited Informal Practices")
        st.markdown(
            """
            - **No Open Burning:** Open incineration of cables, wire harnesses, or circuit boards to recover copper/gold is strictly illegal.
            - **No Acid Leaching:** Backyard chemical stripping using nitric or hydrochloric acid releases toxic fumes into residential neighborhoods.
            - **No Municipal Dumping:** Electronic scrap must never be placed inside black/green household municipal waste bins.
            """
        )
