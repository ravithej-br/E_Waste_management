"""
frontend/views/about.py
───────────────────────
Comprehensive About Us & Services page for EcoScan AI.
Presents the initiative mission, core services, 4-step workflow,
supported materials, and frequently asked questions in a clean SaaS layout.
"""

import streamlit as st


def render_about_page():
    """Renders the About Us, Services, and Platform Fundamentals page."""
    # Header
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1>ℹ️ About Us & Services</h1>
                <p>Learn about our environmental mission, core platform capabilities, and safe recycling services.</p>
            </div>
            <span class="privacy-pill">🌱 Clean Tech Initiative</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_about, tab_services, tab_workflow, tab_faq = st.tabs([
        "🏢 About Us & Mission",
        "🛠️ Our Services",
        "🔄 How It Works",
        "❓ FAQs & Support",
    ])

    # ── TAB 1: About Us & Mission ─────────────────────────────────────────────
    with tab_about:
        col_m1, col_m2 = st.columns([1.2, 1], gap="large")

        with col_m1:
            st.markdown("### 🌿 Our Mission")
            st.markdown(
                """
                **EcoScan AI** is an intelligent civic and environmental technology platform designed to tackle 
                one of India's fastest-growing environmental crises: **unscientific electronic waste disposal**.

                Every year, India produces over **3.2 million metric tonnes of electronic waste**. Historically, more than 
                **90% of discarded electronics** have ended up in the informal sector, where hazardous practices like 
                open cable burning, acid bath extraction, and municipal dumping release neurotoxic lead, mercury vapor, 
                and persistent organic pollutants into our soil, air, and groundwater aquifers.

                Our mission is to empower citizens, educational institutions, and businesses with **instant AI identification**, 
                **statutory hazard awareness**, and **direct routing to state-authorized recycling facilities**.
                """
            )

            st.markdown("---")
            st.markdown("### 🎯 Core Principles")
            st.markdown(
                """
                - **Environmental Stewardship:** Ensuring hazardous materials like lithium, mercury, and lead never reach unlined landfills.
                - **Circular Resource Recovery:** Promoting the formal recovery of precious and critical raw materials (Gold, Copper, Cobalt, Tantalum).
                - **Privacy-First Design:** Strict zero-disk image persistence — scans are evaluated in volatile RAM and immediately discarded.
                - **Statutory Alignment:** Fully compliant with the Government of India E-Waste (Management) Rules 2022.
                """
            )

        with col_m2:
            st.markdown(
                """
                <div class="dark-card" style="margin-bottom: 14px;">
                    <h4 style="margin: 0 0 6px 0; color: #ffffff;">📍 Bengaluru Pilot Hub</h4>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0; line-height: 1.5;">
                        Bengaluru produces over 90,000 tonnes of e-waste annually as India's technology capital. 
                        EcoScan AI directly maps Karnataka State Pollution Control Board (KSPCB) certified facilities across 
                        key corridors including Peenya, Whitefield, Bommasandra, and Yelahanka.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="dark-card">
                    <h4 style="margin: 0 0 6px 0; color: #ffffff;">🔒 Zero Disk Leak Guarantee</h4>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0; line-height: 1.5;">
                        We believe environmental intelligence should never compromise user privacy. 
                        Photographs taken with your phone or webcam are never saved to disk, uploaded to cloud storage, 
                        or used to train external models without consent.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── TAB 2: Our Services ───────────────────────────────────────────────────
    with tab_services:
        st.markdown("### 🛠️ Platform Capabilities & Services")
        st.markdown("Explore the core features designed to assist citizens and organizations with responsible e-waste management.")

        col_s1, col_s2 = st.columns(2, gap="medium")

        with col_s1:
            st.markdown(
                """
                <div class="dark-card" style="height: 100%;">
                    <div style="font-size: 1.8rem; margin-bottom: 8px;">📸</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff; font-size: 1.05rem;">1. AI Visual Classification</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 10px; line-height: 1.5;">
                        Instant edge neural classification of electronic items from your device camera or file dropzone. 
                        Recognizes batteries, CFL lamps, CRT monitors, circuit boards, smartphones, and computer peripherals.
                    </p>
                    <span style="font-size: 0.72rem; color: #10b981; font-weight: 600; text-transform: uppercase;">
                        ✓ Sub-10ms Inference • 7 Class Categories
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_s2:
            st.markdown(
                """
                <div class="dark-card" style="height: 100%;">
                    <div style="font-size: 1.8rem; margin-bottom: 8px;">🧪</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff; font-size: 1.05rem;">2. Statutory Hazard Assessment</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 10px; line-height: 1.5;">
                        Automated toxicity screening under India E-Waste Rules 2022. Automatically highlights hazardous substances 
                        like elemental mercury vapor, lead oxide funnel glass, lithium electrolyte, and brominated flame retardants.
                    </p>
                    <span style="font-size: 0.72rem; color: #10b981; font-weight: 600; text-transform: uppercase;">
                        ✓ Chemical Profiling • Risk Categorization
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        col_s3, col_s4 = st.columns(2, gap="medium")

        with col_s3:
            st.markdown(
                """
                <div class="dark-card" style="height: 100%;">
                    <div style="font-size: 1.8rem; margin-bottom: 8px;">📍</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff; font-size: 1.05rem;">3. Authorized Recycler Locator</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 10px; line-height: 1.5;">
                        Search certified KSPCB & CPCB dismantlers ranked by geographic distance using the Haversine formula. 
                        Includes verified operating hours, directions, telephone numbers, and material intake criteria.
                    </p>
                    <span style="font-size: 0.72rem; color: #10b981; font-weight: 600; text-transform: uppercase;">
                        ✓ Interactive Map • Material Filtering
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_s4:
            st.markdown(
                """
                <div class="dark-card" style="height: 100%;">
                    <div style="font-size: 1.8rem; margin-bottom: 8px;">📋</div>
                    <h4 style="margin: 0 0 6px 0; color: #ffffff; font-size: 1.05rem;">4. Audit & History Hub</h4>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 10px; line-height: 1.5;">
                        Keep track of your electronic waste inspections with a dedicated audit log. 
                        Filter by date, category, or hazard rating, and export audit trails to CSV for institutional ESG compliance.
                    </p>
                    <span style="font-size: 0.72rem; color: #10b981; font-weight: 600; text-transform: uppercase;">
                        ✓ CSV Export • Filterable Audit Trail
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── TAB 3: How It Works ───────────────────────────────────────────────────
    with tab_workflow:
        st.markdown("### 🔄 The 4-Step E-Waste Lifecycle")
        st.markdown("How EcoScan AI guides you from an obsolete gadget to safe, certified circular recovery:")

        steps_data = [
            ("1", "📸 Provide Photo", "Capture an image of your old device, battery, or circuit board using your camera or upload a file. Use our Framing Zoom or Focus Mode if the item is on a reflective table."),
            ("2", "⚡ Neural Evaluation", "The quantized ONNX vision engine processes the item in volatile RAM. It matches visual feature representations against calibrated e-waste classification profiles."),
            ("3", "🛡️ Review Safety Dossier", "Inspect the identified material class, confidence match, toxic chemicals present, and critical DOs/DONTs handling checklists to avoid fire or toxicity risks."),
            ("4", "📍 Connect with Recycler", "Click 'Find Nearest Recycler' to view certified KSPCB centers accepting your item. Check their opening hours, phone ahead for bulk drop-offs, and obtain EPR receipts."),
        ]

        for num, title, desc in steps_data:
            st.markdown(
                f"""
                <div class="dark-card" style="display: flex; align-items: flex-start; gap: 16px; margin-bottom: 12px;">
                    <div style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                                font-weight: 800; font-size: 1.1rem; width: 36px; height: 36px; border-radius: 50%;
                                display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">
                        {num}
                    </div>
                    <div>
                        <h4 style="margin: 0 0 4px 0; color: #ffffff; font-size: 1rem;">{title}</h4>
                        <p style="margin: 0; font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">{desc}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── TAB 4: FAQs & Support ─────────────────────────────────────────────────
    with tab_faq:
        st.markdown("### ❓ Frequently Asked Questions")

        with st.expander("Which categories of e-waste are currently supported?", expanded=True):
            st.markdown(
                """
                EcoScan AI specializes in seven statutory e-waste streams:
                1. **Batteries:** Li-ion, Lead-Acid, NiMH, AA/AAA household cells.
                2. **CFL / Fluorescent Bulbs:** Spiral compact fluorescent lamps, linear mercury tubes.
                3. **CRT Monitors:** Cathode ray tube displays, bulky legacy TVs.
                4. **Printed Circuit Boards (PCBs):** Motherboards, graphic cards, RAM modules, embedded boards.
                5. **Mobile Phones:** Smartphones, feature phones, hand-held electronics.
                6. **Keyboards & Peripherals:** Keyboards, mice, desktop peripheral accessories.
                7. **Other / Unclassified E-Waste:** General electronic scrap and mixed components.
                """
            )

        with st.expander("Why can't I just throw small batteries into municipal waste?", expanded=False):
            st.markdown(
                """
                Batteries contain concentrated heavy metals (lead, cadmium, cobalt) and combustible lithium. 
                When compressed in municipal garbage trucks or exposed to moisture in unlined landfills, 
                they can spark **landfill fires** and leach toxic acids directly into groundwater supplies. 
                Under India's **Battery Waste Management Rules 2022**, 100% formal recovery is legally mandated.
                """
            )

        with st.expander("Does EcoScan AI charge any fee for finding recyclers?", expanded=False):
            st.markdown(
                """
                **No.** EcoScan AI is a free civic and academic service. All directory information is compiled 
                from official public registry records of the **Karnataka State Pollution Control Board (KSPCB)** 
                and the **Central Pollution Control Board (CPCB)** for public benefit.
                """
            )

        with st.expander("What should I do if an electronic item or battery is swollen or leaking?", expanded=False):
            st.markdown(
                """
                1. **Do not pierce or drop** the battery.
                2. Place it in a non-conductive, fireproof container (such as a metal tin with dry sand).
                3. Wear gloves and do not inhale any venting vapors.
                4. Contact an authorized hazardous waste collection hub immediately for emergency neutralization.
                """
            )

        st.markdown(
            """
            <div style="margin-top: 24px; padding: 14px 18px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; font-size: 0.82rem; color: #94a3b8;">
                💬 <b>Need assistance or have feedback?</b> For academic inquiries or to list new KSPCB authorized facilities, contact the development team at the Department of Computer Science & Engineering, Bengaluru, Karnataka.
            </div>
            """,
            unsafe_allow_html=True,
        )
