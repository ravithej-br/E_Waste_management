"""
frontend/views/regulations.py
─────────────────────────────
Comprehensive statutory framework and compliance directory under
Government of India E-Waste (Management) Rules 2022 & Battery Waste Management Rules 2022.
Structured into organized tabs and collapsible expanders.
"""

import streamlit as st
import pandas as pd
from frontend.components.badges import render_hazard_badge

HAZARD_MATRIX = [
    {
        "category": "battery",
        "name": "Battery (Li-ion / Lead-Acid)",
        "hazard_level": "CRITICAL",
        "toxins": "Lithium, Cobalt, Sulfuric Acid, Lead, Cadmium",
        "hazards": "Thermal runaway fire explosion, groundwater acid contamination",
        "statute": "Battery Waste Rules 2022",
        "details": "Under GSR 664(E), 100% recovery of critical battery raw materials is mandatory. Dumping lead-acid or lithium batteries in unlined landfills is strictly punishable."
    },
    {
        "category": "cfl_bulb",
        "name": "CFL / Fluorescent Lamp",
        "hazard_level": "HIGH",
        "toxins": "Elemental Mercury vapor, Phosphor dust",
        "hazards": "Severe neurotoxicity upon glass breakage and vapor inhalation",
        "statute": "E-Waste Rules Schedule I (ITEW20)",
        "details": "Contains 3–5 mg of elemental mercury per bulb. Closed-loop retort recovery systems are required under CPCB guidelines to prevent atmospheric vapor release."
    },
    {
        "category": "monitor_crt",
        "name": "Cathode Ray Tube (CRT) Monitor",
        "hazard_level": "HIGH",
        "toxins": "Lead oxide funnel glass (1–2 kg), Barium",
        "hazards": "Vacuum implosion hazard; lead poisoning upon landfill leaching",
        "statute": "E-Waste Rules Schedule I (ITEW1)",
        "details": "Funnel glass contains up to 25% lead oxide by weight. Informal smashing creates respirable toxic dust and bioaccumulative lead leachate."
    },
    {
        "category": "pcb",
        "name": "Printed Circuit Board (PCB)",
        "hazard_level": "HIGH",
        "toxins": "Lead solder, Brominated Flame Retardants (PBDEs), Copper",
        "hazards": "Dioxin release from open burning; persistent bioaccumulative chemicals",
        "statute": "E-Waste Rules Schedule I (ITEW2)",
        "details": "Open backyard smelting generates halogenated dioxins and furans. Industrial hydrometallurgical recovery recovers 99%+ gold/copper safely."
    },
    {
        "category": "mobile_phone",
        "name": "Smartphone / Mobile Phone",
        "hazard_level": "MODERATE",
        "toxins": "Lithium-Cobalt battery, Gold, Tantalum, Arsenic",
        "hazards": "Combustible micro-battery; depletion of strategic rare earth minerals",
        "statute": "E-Waste Rules Schedule I (ITEW15)",
        "details": "Requires certified EPR channel take-back. Contains valuable trace elements requiring closed shredding and hydrometallurgical extraction."
    },
    {
        "category": "keyboard",
        "name": "Keyboard / Peripherals",
        "hazard_level": "LOW",
        "toxins": "ABS plastics, Polybrominated biphenyls",
        "hazards": "Microplastic generation, persistent halogenated flame retardants",
        "statute": "E-Waste Rules Schedule I (ITEW4)",
        "details": "High mechanical recyclability. Thermoplastics must be shredded and pelletized without toxic open incineration."
    },
]


def render_regulations_page():
    """Renders the statutory guidelines organized into tabs and expanders."""
    st.markdown(
        """
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>⚖️ Statutory Framework & Legal Guidelines</h1>
                    <p>Government of India E-Waste (Management) Rules 2022 & Environmental Protection Acts.</p>
                </div>
                <span class="privacy-pill">📜 MoEFCC GSR 816(E)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_overview, tab_matrix, tab_epr, tab_protocols = st.tabs([
        "📜 Statutory Overview",
        "🧪 Hazard & Chemical Matrix",
        "🏢 EPR & Legal Penalties",
        "🛡️ Consumer Protocols",
    ])

    # TAB 1: Statutory Overview
    with tab_overview:
        col_c1, col_c2, col_c3 = st.columns(3, gap="medium")
        with col_c1:
            st.markdown(
                """
                <div class="dark-card">
                    <div style="font-size: 1.5rem; margin-bottom: 6px;">📜</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff;">E-Waste Rules, 2022</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0;">
                        Notified by MoEFCC via GSR 816(E). Covers all electrical & electronic equipment across 106 distinct item categories.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_c2:
            st.markdown(
                """
                <div class="dark-card">
                    <div style="font-size: 1.5rem; margin-bottom: 6px;">🔋</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff;">Battery Waste Rules</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0;">
                        Notified under GSR 664(E). Mandates 100% recovery of critical elements (Lithium, Cobalt, Nickel, Lead).
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_c3:
            st.markdown(
                """
                <div class="dark-card">
                    <div style="font-size: 1.5rem; margin-bottom: 6px;">🚨</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff;">Section 15 Penalties</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0;">
                        Environment (Protection) Act, 1986. Imprisonment up to 5 years, ₹1,00,000 fine for illegal disposal or open burning.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("📌 Key Regulatory Provisions & Statutory Milestones", expanded=True):
            st.markdown(
                """
                - **Universal Coverage:** Extends beyond IT hardware to medical devices, photovoltaic solar panels, and consumer electronics.
                - **Digital EPR Tracking:** All trade in recycling credits must occur through the Central Pollution Control Board (CPCB) online portal.
                - **Formalized Dismantler Hierarchy:** Aggregators are permitted only to collect; dismantling and chemical refining require specialized KSPCB consent to operate.
                """
            )

    # TAB 2: Hazard & Chemical Matrix
    with tab_matrix:
        st.markdown("### Statutory Classification & Chemical Hazard Matrix")

        df_display = pd.DataFrame([
            {
                "E-Waste Category": item["name"],
                "Hazard Level": item["hazard_level"],
                "Target Toxins": item["toxins"],
                "Primary Hazards": item["hazards"],
                "Statutory Schedule": item["statute"],
            }
            for item in HAZARD_MATRIX
        ])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("#### Detailed Material Dossiers")
        for item in HAZARD_MATRIX:
            with st.expander(f"{item['name']} — {item['hazard_level']} Hazard Assessment", expanded=False):
                st.markdown(f"**Identified Toxic Compounds:** `{item['toxins']}`")
                st.markdown(f"**Hazard Manifestation:** {item['hazards']}")
                st.markdown(f"**Governing Rule:** `{item['statute']}`")
                st.info(item["details"])

    # TAB 3: EPR & Legal Penalties
    with tab_epr:
        col_e1, col_e2 = st.columns(2, gap="large")
        with col_e1:
            st.markdown("### 🏢 Extended Producer Responsibility (EPR)")
            st.markdown(
                """
                Under Chapter II of E-Waste Rules 2022:
                - **Registration Requirement:** Every electronic producer, importer, and brand owner must be registered on the national CPCB EPR portal.
                - **Take-Back Quotas:** Producers are legally required to collect and recycle escalating targets (up to 80% of average product lifespans).
                - **EPR Certificates:** Compliance is tracked via verifiable, audited recycling credits issued by certified e-waste recyclers.
                """
            )
        with col_e2:
            st.markdown("### ⚖️ Judicial Penalties (Section 15, EPA 1986)")
            st.markdown(
                """
                Non-compliance triggers statutory enforcement:
                - **Imprisonment:** Up to **5 years** for unauthorized dumping or illegal burning of electronic waste.
                - **Financial Penalties:** Fines up to **₹1,00,000**, with additional penalties of **₹5,000 per day** for continuous infractions.
                - **Environmental Compensation:** CPCB levying of punitive restoration damages for contamination of soil and groundwater aquifers.
                """
            )

    # TAB 4: Consumer Protocols
    with tab_protocols:
        st.markdown("### 🛡️ Consumer Handling Checklist & Prohibited Practices")
        with st.expander("✅ Citizen Responsibilities & Handover Procedures", expanded=True):
            st.markdown(
                """
                1. **Never Mix with General Refuse:** Segregate all spent electronics from wet/dry municipal trash bins.
                2. **Insulate Battery Terminals:** Cover exposed contacts with tape to prevent short-circuit sparks in transport.
                3. **Wipe Personal Data:** Factory-reset all smartphones and laptops prior to drop-off.
                4. **Request EPR Manifest:** Obtain a recycling slip or acknowledgment from the collection depot.
                """
            )

        with st.expander("❌ Strictly Prohibited Informal Methods", expanded=True):
            st.markdown(
                """
                - **No Open Burning:** Open cable burning produces carcinogenic dioxins and neurotoxic lead particulate.
                - **No Acid Bath Stripping:** Nitric acid leaching in residential zones pollutes stormwater runoff.
                - **No CRT Screen Smashes:** Breaking vacuum tubes disperses toxic lead and barium phosphor dust.
                """
            )
