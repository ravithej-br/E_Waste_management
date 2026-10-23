"""
frontend/views/benchmarks.py
────────────────────────────
Empirical benchmarks, model comparisons, ONNX latency analysis,
and temperature calibration metrics for the academic project report.
"""

import streamlit as st
import pandas as pd


def render_benchmarks_page():
    """Renders empirical benchmarks, latency tests, and calibration curves."""
    st.markdown(
        """
        <div class="hero-banner">
            <h1>📊 System Architecture & Empirical Benchmarks</h1>
            <p>Empirical evaluation across PyTorch FP32, ONNX Runtime, Selective INT8 Quantization, and Calibration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Quick Stat Metric Cards
    col_s1, col_s2, col_s3, col_s4 = st.columns(4, gap="medium")
    with col_s1:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">90.07%</div>
                <div class="stat-label">Production Test Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">100.0%</div>
                <div class="stat-label">Hazard Recall (Batteries/CFL)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s3:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">5.03 ms</div>
                <div class="stat-label">CPU Inference Latency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s4:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">2.89%</div>
                <div class="stat-label">Calibrated ECE Error</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    col_t1, col_t2 = st.columns(2, gap="large")

    with col_t1:
        st.markdown("### 🏆 Model Comparison on Stratified Test Set")
        model_data = [
            {"Model Architecture": "EfficientNet-B0 (PyTorch FP32)", "Size": "15.61 MB", "Test Acc": "90.22%", "Hazard Recall": "100.0%", "CPU Latency": "21.28 ms"},
            {"Model Architecture": "EfficientNet-B0 (Selective ONNX INT8)", "Size": "15.29 MB", "Test Acc": "90.07%", "Hazard Recall": "100.0%", "CPU Latency": "5.03 ms"},
            {"Model Architecture": "MobileNetV3-Small (PyTorch FP32)", "Size": "5.95 MB", "Test Acc": "88.35%", "Hazard Recall": "100.0%", "CPU Latency": "6.82 ms"},
            {"Model Architecture": "MobileNetV3-Small (ONNX FP32)", "Size": "5.82 MB", "Test Acc": "88.35%", "Hazard Recall": "100.0%", "CPU Latency": "1.49 ms"},
        ]
        st.dataframe(pd.DataFrame(model_data), use_container_width=True, hide_index=True)

        st.markdown("### 🔬 Post-Hoc Temperature Calibration")
        st.markdown(
            """
            - **Uncalibrated Baseline:** Expected Calibration Error (ECE) was **20.20%**, causing the network to be overconfident on out-of-distribution electronic clutter.
            - **Optimal Temperature Derived:** $T^* = 0.4923$ minimizing Negative Log-Likelihood (NLL).
            - **Post-Calibration ECE:** **2.89%** (**85.7% relative reduction** in calibration error).
            - **Safeguard Cutoff:** $0.65$ threshold derived from coverage-accuracy Pareto curve.
            """
        )

    with col_t2:
        st.markdown("### ⚡ End-to-End CPU Latency Breakdown")
        latency_data = [
            {"Pipeline Component": "In-Memory RAM Decode (PIL)", "Duration": "1.85 ms", "Percentage": "21.8%"},
            {"Pipeline Component": "ImageNet Normalization & Resize (224x224)", "Duration": "1.61 ms", "Percentage": "18.9%"},
            {"Pipeline Component": "Selective INT8 ONNX Forward Pass", "Duration": "5.03 ms", "Percentage": "59.3%"},
            {"Pipeline Component": "Temperature Scaling & Distance Ranking", "Duration": "0.12 ms", "Percentage": "1.4%"},
            {"Pipeline Component": "Total In-Memory Response Time", "Duration": "8.61 ms", "Percentage": "100.0%"},
        ]
        st.dataframe(pd.DataFrame(latency_data), use_container_width=True, hide_index=True)

        st.markdown("### 💡 Selective INT8 Quantization Discovery")
        st.markdown(
            """
            Standard naive static INT8 calibration collapsed test accuracy from **90.22% to 7.91%** due to clipping sensitivity in depthwise separable convolution layers.
            By isolating dense parameter matrices (`MatMul`, `Gemm`) into INT8 while preserving depthwise spatial filters in FP32, our selective pipeline preserved **90.07% accuracy** with **4.2x latency acceleration**.
            """
        )
