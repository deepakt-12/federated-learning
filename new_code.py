def health_dashboard_page():
    scaler, model = load_and_prepare()

    if "history" not in st.session_state:
        st.session_state.history = []

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* Premium Dark Theme Variables */
        :root {
            --bg-dark: #0B0F14;
            --bg-card: rgba(20, 25, 35, 0.6);
            --accent-primary: #3ABEFF;
            --accent-secondary: #0A66C2;
            --text-main: #FFFFFF;
            --text-muted: #8E9BAE;
        }

        html, body, p, div, h1, h2, h3, h4, h5, h6, span, label {
            font-family: 'Outfit', sans-serif;
            color: var(--text-main);
        }

        /* Ambient Background */
        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(58, 190, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(10, 102, 194, 0.04) 0%, transparent 50%);
            background-attachment: fixed;
        }
        
        [data-testid="stMainBlockContainer"] {
            padding: 2rem 2.5rem !important;
            max-width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }

        .element-container { margin-bottom: 0px !important; }
        
        /* Compact, Styled Inputs */
        div[data-testid="stNumberInput"] { margin-bottom: -15px !important; }
        .stSlider { padding-bottom: 0px !important; }
        .stSlider > div[data-testid="stWidgetLabel"] p, .stNumberInput > div[data-testid="stWidgetLabel"] p { 
            font-size: 13px !important; color: var(--text-muted) !important; font-weight: 500; letter-spacing: 0.3px;
        }

        /* Glassmorphism CTA Button */
        .stButton>button {
            border-radius: 12px;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 700;
            background: var(--accent-primary);
            color: #0B0F14;
            border: none;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 20px;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(58, 190, 255, 0.4);
            color: #0B0F14;
        }

        .risk-pulse {
            animation: pulse-glow 2s infinite;
        }
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.3); }
            70% { box-shadow: 0 0 0 15px rgba(255, 23, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0); }
        }
        </style>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html("""
    <script>
        const doc = window.parent.document;
        function enforceLayout() {
            const cols = doc.querySelectorAll('div[data-testid="column"]');
            cols.forEach((col) => {
                col.style.background = 'linear-gradient(145deg, rgba(25,30,40,0.7) 0%, rgba(15,18,25,0.8) 100%)';
                col.style.backdropFilter = 'blur(20px)';
                col.style.webkitBackdropFilter = 'blur(20px)';
                col.style.border = '1px solid rgba(255, 255, 255, 0.05)';
                col.style.borderTop = '1px solid rgba(255, 255, 255, 0.1)';
                col.style.borderRadius = '24px';
                col.style.padding = '30px';
                col.style.height = 'calc(100vh - 64px)';
                col.style.overflow = 'hidden';
                col.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
                col.style.transition = 'all 0.3s ease';
            });
            const blocks = doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if (blocks.length > 0) blocks[0].style.gap = '24px';
        }
        enforceLayout();
        setTimeout(enforceLayout, 500);
    </script>
    """, height=0, width=0)

    # REVERTED TO 3 COLUMN THEME (1.1, 1.8, 1.1)
    col1, col2, col3 = st.columns([1.1, 1.8, 1.1], gap="medium")

    with col1:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:20px;'>Patient Vitals</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: age = st.number_input("Age", 0, 100, 33)
        with c2: gender = st.selectbox("Sex", ["Female", "Male"])
        
        c3, c4 = st.columns(2)
        with c3: height = st.number_input("Height (cm)", 100, 220, 170)
        with c4: weight = st.number_input("Weight (kg)", 30, 150, 70)
        
        bmi = round(weight / ((height/100) ** 2), 2)
        
        glucose = st.slider("Glucose Level", 40, 250, st.session_state.get('glucose_val', 100), key='glucose_val')
        blood_pressure = st.slider("Blood Pressure", 0, 160, st.session_state.get('bp_val', 70), key='bp_val')
        
        # PROPORTIONAL RANGES
        max_insulin_allowed = min(900, int(glucose * 3.5 + 50))
        min_insulin_allowed = max(0, int(glucose * 0.1))
        # Safely assign bounds
        ins_val = st.session_state.get('insulin_val', min_insulin_allowed + 20)
        if hasattr(ins_val, 'value'): ins_val = ins_val.value
        try:
            ins_val = max(min_insulin_allowed, min(int(ins_val), max_insulin_allowed))
        except:
            ins_val = min_insulin_allowed
            
        insulin = st.slider("Insulin", min_insulin_allowed, max_insulin_allowed, ins_val, key='insulin_val')
        
        max_skin_allowed = min(100, int(bmi * 1.8 + 10))
        min_skin_allowed = max(0, int(bmi * 0.3 - 5))
        skn_val = st.session_state.get('skin_val', 20)
        try:
            skn_val = max(min_skin_allowed, min(int(skn_val), max_skin_allowed))
        except:
            skn_val = min_skin_allowed
            
        skin_thickness = st.slider("Skin Thickness", min_skin_allowed, max_skin_allowed, skn_val, key='skin_val')
        dpf = st.slider("Pedigree Function", 0.0, 3.0, st.session_state.get('dpf_val', 0.5), key='dpf_val')
        pregnancies = 0 if gender == "Male" else st.slider("Pregnancies", 0, 20, st.session_state.get('preg_val', 0), key='preg_val')
        
        input_data = pd.DataFrame([[
            pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age
        ]], columns=["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"])
        
        run_diag = st.button("PREDICT RISK")

    with col2:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:24px;'>Diagnostic Output</div>", unsafe_allow_html=True)
        pred_container = st.empty()
        insight_container = st.empty()
        
        if run_diag and model is not None:
            input_scaled = scaler.transform(input_data)
            prediction_prob = model.predict(input_scaled)[0][0]
            
            with pred_container.container():
                if prediction_prob >= 0.7:
                    risk_txt, color, bg, pulse = "HIGH RISK", "#FF1744", "rgba(255, 23, 68, 0.15)", "risk-pulse"
                elif prediction_prob >= 0.4:
                    risk_txt, color, bg, pulse = "MEDIUM RISK", "#FFD600", "rgba(255, 214, 0, 0.15)", ""
                else:
                    risk_txt, color, bg, pulse = "LOW RISK", "#00E676", "rgba(0, 230, 118, 0.15)", ""
                
                # Previous icons requested by user:
                icon = f'<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
                
                st.markdown(f"""
                    <div class="{pulse}" style="background:{bg}; border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:40px; text-align:center; height:260px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                        <div style="margin-bottom:20px;">{icon}</div>
                        <div style="font-size:13px; font-weight:700; color:{color}; text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">Classification</div>
                        <div style="font-size:56px; font-weight:800; color:{color}; line-height:1;">{risk_txt}</div>
                        <div style="font-size:20px; font-weight:500; color:#FFFFFF; margin-top:12px;">{(prediction_prob*100):.1f}% AI Confidence</div>
                    </div>
                """, unsafe_allow_html=True)
                
            import datetime
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.history.insert(0, (ts, f"{(prediction_prob*100):.1f}%", risk_txt, color))
            if len(st.session_state.history) > 4:
                st.session_state.history.pop()
                
            with insight_container.container():
                history_html = "".join([f'<div style="font-size:13px; color:#8E9BAE; margin-bottom:12px; display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;"><span>{h[0]}</span><span style="color:{h[3]}; font-weight:700;">{h[2]} ({h[1]})</span></div>' for h in st.session_state.history])
                st.markdown(f"""
                    <div style="margin-top:40px; display:flex; gap:40px;">
                        <div style="flex:1;">
                            <div style="font-size:16px; font-weight:700; color:#FFFFFF; margin-bottom:16px;">Clinical Insights</div>
                            <ul style="color:#8E9BAE; font-size:14px; line-height:1.8; padding-left:16px; margin:0;">
                                <li>{ "Critical: Fasting glucose elevated." if glucose > 140 else "Stable: Glucose levels within bounds." }</li>
                                <li>{ "Warning: BMI indicates risk factor." if bmi > 30 else "Stable: BMI threshold is nominal." }</li>
                                <li>{ "Stable: BP normal." if blood_pressure < 80 else "Warning: Indications of hypertensive stress." }</li>
                            </ul>
                        </div>
                        <div style="flex:1;">
                            <div style="font-size:16px; font-weight:700; color:#FFFFFF; margin-bottom:16px;">Past Predictions</div>
                            {history_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            with pred_container.container():
                st.markdown("""
                    <div style="border:1px dashed rgba(255,255,255,0.2); background:rgba(255,255,255,0.02); border-radius:20px; padding:40px; text-align:center; height:260px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:20px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                        <div style="font-size:15px; font-weight:500; color:#8E9BAE; text-transform:uppercase;">System Standby</div>
                        <div style="font-size:28px; font-weight:700; color:#FFFFFF; margin-top:8px;">Ready to Analyze</div>
                    </div>
                """, unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:20px;'>Analysis Matrix</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius:14px; padding:18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">GLUCOSE LEVEL</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{glucose} <span style="font-size:13px; color:#64748B; font-weight:500;">mg/dL</span></div>
                </div>
                <div style="background:{'rgba(255, 23, 68, 0.2)' if glucose>140 else 'rgba(0, 230, 118, 0.2)'}; height:12px; width:12px; border-radius:50%; border:2px solid {'#FF1744' if glucose>140 else '#00E676'}; box-shadow: 0 0 10px {'rgba(255,23,68,0.5)' if glucose>140 else 'rgba(0,230,118,0.5)'};"></div>
            </div>
            
            <div style="background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius:14px; padding:18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">BODY MASS INDEX</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{bmi} <span style="font-size:13px; color:#64748B; font-weight:500;">kg/m²</span></div>
                </div>
                <div style="background:{'rgba(255, 23, 68, 0.2)' if bmi>30 else 'rgba(0, 230, 118, 0.2)'}; height:12px; width:12px; border-radius:50%; border:2px solid {'#FF1744' if bmi>30 else '#00E676'}; box-shadow: 0 0 10px {'rgba(255,23,68,0.5)' if bmi>30 else 'rgba(0,230,118,0.5)'};"></div>
            </div>
            
            <div style="background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius:14px; padding:18px; margin-bottom:32px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">PATIENT AGE</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{age} <span style="font-size:13px; color:#64748B; font-weight:500;">yrs</span></div>
                </div>
                <div style="background:rgba(58, 190, 255, 0.2); height:12px; width:12px; border-radius:50%; border:2px solid #3ABEFF; box-shadow: 0 0 10px rgba(58,190,255,0.5);"></div>
            </div>
            
            <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-bottom:20px; letter-spacing:0.5px;">Vector Impact Weights</div>
            
            <div style="font-size:12px; font-weight:600; color:#8E9BAE; letter-spacing:0.5px;">
                <div style="margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>GLUCOSE</span><span style="color:#3ABEFF;">85%</span></div>
                    <div style="background:rgba(255,255,255,0.05); height:6px; border-radius:3px; overflow:hidden;"><div style="background:#3ABEFF; width:85%; height:100%; border-radius:3px;"></div></div>
                </div>
                <div style="margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>BMI</span><span style="color:#3ABEFF;">65%</span></div>
                    <div style="background:rgba(255,255,255,0.05); height:6px; border-radius:3px; overflow:hidden;"><div style="background:#3ABEFF; width:65%; height:100%; border-radius:3px;"></div></div>
                </div>
                <div style="margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>AGE</span><span style="color:#3ABEFF;">50%</span></div>
                    <div style="background:rgba(255,255,255,0.05); height:6px; border-radius:3px; overflow:hidden;"><div style="background:#3ABEFF; width:50%; height:100%; border-radius:3px;"></div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
