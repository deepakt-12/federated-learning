def model_comparison_page():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --bg-dark: #0B0F14;
            --accent-primary: #3ABEFF;
            --text-main: #FFFFFF;
        }
        
        html, body, p, div, h1, h2, h3, h4, h5, h6, span, label {
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-main);
        }
        
        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(58, 190, 255, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(10, 102, 194, 0.05) 0%, transparent 50%);
            background-attachment: fixed;
        }
        
        /* Glassmorphism Cards */
        .metric-card {
            background: linear-gradient(145deg, rgba(25,30,40,0.6) 0%, rgba(15,18,25,0.8) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:32px; font-weight:800; color:#FFFFFF; margin-bottom:10px; letter-spacing: -0.5px;'>Model Performance Comparison</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:15px; color:#8E9BAE; margin-bottom:30px;'>Compare Centralized vs Federated predictive models across critical accuracy thresholds.</div>", unsafe_allow_html=True)

    X_test_scaled, y_test, feature_cols = load_eval_data()
    cen_model, fed_model = load_models_for_comparison()

    if cen_model is None and fed_model is None:
        st.error("No models found. Expected: models/centralized_model.keras and/or models/federated_model.keras")
        return

    st.sidebar.markdown("### Comparison Settings")
    threshold = st.sidebar.slider("Decision Threshold", 0.1, 0.9, 0.5, 0.05)

    cen_metrics = compute_metrics_from_model(cen_model, X_test_scaled, y_test, threshold=threshold)
    fed_metrics = compute_metrics_from_model(fed_model, X_test_scaled, y_test, threshold=threshold)

    rows = []
    if cen_metrics is not None:
        rows.append({
            "Model": "Centralized",
            "Accuracy": cen_metrics["accuracy"],
            "Precision": cen_metrics["precision"],
            "Recall": cen_metrics["recall"],
            "F1-Score": cen_metrics["f1"],
            "TP": cen_metrics["tp"],
            "TN": cen_metrics["tn"],
            "FP": cen_metrics["fp"],
            "FN": cen_metrics["fn"],
        })
    if fed_metrics is not None:
        rows.append({
            "Model": "Federated",
            "Accuracy": fed_metrics["accuracy"],
            "Precision": fed_metrics["precision"],
            "Recall": fed_metrics["recall"],
            "F1-Score": fed_metrics["f1"],
            "TP": fed_metrics["tp"],
            "TN": fed_metrics["tn"],
            "FP": fed_metrics["fp"],
            "FN": fed_metrics["fn"],
        })

    df = pd.DataFrame(rows).set_index("Model")

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:15px; letter-spacing:0.5px;'>Metrics Table</div>", unsafe_allow_html=True)
        st.dataframe(df.style.format({
            "Accuracy": "{:.4f}",
            "Precision": "{:.4f}",
            "Recall": "{:.4f}",
            "F1-Score": "{:.4f}",
        }), use_container_width=True)

    with c2:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:15px; letter-spacing:0.5px;'>Comparison Chart</div>", unsafe_allow_html=True)
        try:
            import plotly.graph_objects as go
            metrics_to_plot = ["Accuracy", "Precision", "Recall", "F1-Score"]
            fig = go.Figure()

            if cen_metrics is not None:
                fig.add_trace(go.Bar(
                    name="Centralized",
                    x=metrics_to_plot,
                    y=[df.loc["Centralized", m] for m in metrics_to_plot],
                    marker_color='#3ABEFF'
                ))
            if fed_metrics is not None:
                fig.add_trace(go.Bar(
                    name="Federated",
                    x=metrics_to_plot,
                    y=[df.loc["Federated", m] for m in metrics_to_plot],
                    marker_color='#8E9BAE'
                ))

            fig.update_layout(
                barmode="group",
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis=dict(range=[0, 1], gridcolor='rgba(255,255,255,0.05)', title_font=dict(color='#8E9BAE')),
                xaxis=dict(tickfont=dict(color='#8E9BAE')),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#FFFFFF'), bgcolor='rgba(0,0,0,0)', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Plotly chart could not be rendered.")

    st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-top:20px; margin-bottom:20px; letter-spacing:0.5px;'>Confusion Matrix Analysis</div>", unsafe_allow_html=True)
    m1, m2 = st.columns(2, gap="large")

    def render_cm_card(title, metrics, border_color):
        if metrics is None:
            return f"<div class='metric-card'>Model not found.</div>"
        return f'''
            <div class="metric-card" style="border-top: 2px solid {border_color};">
                <div style="font-size:14px; font-weight:700; color:#8E9BAE; letter-spacing:1px; margin-bottom:16px; text-transform:uppercase;">{title} Model</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <div><span style="color:#00E676; font-weight:800; font-size:24px;">{metrics['tp']}</span><br><span style="font-size:11px; color:#8E9BAE;">True Positive</span></div>
                    <div style="text-align:right;"><span style="color:#FF1744; font-weight:800; font-size:24px;">{metrics['fp']}</span><br><span style="font-size:11px; color:#8E9BAE;">False Positive</span></div>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <div><span style="color:#FF1744; font-weight:800; font-size:24px;">{metrics['fn']}</span><br><span style="font-size:11px; color:#8E9BAE;">False Negative</span></div>
                    <div style="text-align:right;"><span style="color:#00E676; font-weight:800; font-size:24px;">{metrics['tn']}</span><br><span style="font-size:11px; color:#8E9BAE;">True Negative</span></div>
                </div>
            </div>
        '''

    with m1:
        st.markdown(render_cm_card("Centralized", cen_metrics, "#3ABEFF"), unsafe_allow_html=True)
    with m2:
        st.markdown(render_cm_card("Federated", fed_metrics, "#8E9BAE"), unsafe_allow_html=True)
