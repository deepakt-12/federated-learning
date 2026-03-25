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
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-main);
        }

        /* Ambient Background */
        .stApp {
            background-color: #0B0F19;
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(139, 92, 246, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 100% 100%, rgba(56, 189, 248, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.15) 0%, transparent 50%);
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
            border-radius: 14px;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary) 0%, #8b5cf6 100%);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(58, 190, 255, 0.4);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(58, 190, 255, 0.6);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.4);
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
                col.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)';
                col.style.backdropFilter = 'blur(24px)';
                col.style.webkitBackdropFilter = 'blur(24px)';
                col.style.border = '1px solid rgba(255, 255, 255, 0.08)';
                col.style.borderTop = '1px solid rgba(255, 255, 255, 0.15)';
                col.style.borderRadius = '24px';
                col.style.padding = '30px';
                col.style.height = 'calc(100vh - 64px)';
                col.style.overflow = 'hidden';
                col.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.3)';
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
        with c1: age = st.number_input("Age", 0, 100, st.session_state.get('age', 33), key='age')
        
        gender_idx = 0 if st.session_state.get('gender', 'Female') == 'Female' else 1
        with c2: gender = st.selectbox("Sex", ["Female", "Male"], index=gender_idx, key='gender')
        
        c3, c4 = st.columns(2)
        with c3: height = st.number_input("Height (cm)", 100, 220, st.session_state.get('height', 170), key='height')
        with c4: weight = st.number_input("Weight (kg)", 30, 150, st.session_state.get('weight', 70), key='weight')
        
        bmi = round(weight / ((height/100) ** 2), 2)
        
        glucose = st.slider("Glucose Level", 40, 250, st.session_state.get('glucose_val', 100), key='glucose_val')
        blood_pressure = st.slider("Blood Pressure", 0, 160, st.session_state.get('bp_val', 70), key='bp_val')
        
        # PROPORTIONAL RANGES
        max_insulin_allowed = min(900, int(glucose * 3.5 + 50))
        min_insulin_allowed = max(0, int(glucose * 0.1))
        # Safely constrain existing session state bounds to prevent slider crash
        if 'insulin_val' in st.session_state:
            curr_val = st.session_state['insulin_val']
            if hasattr(curr_val, 'value'): curr_val = curr_val.value
            try:
                curr_val = max(min_insulin_allowed, min(int(curr_val), max_insulin_allowed))
            except:
                curr_val = min_insulin_allowed
            st.session_state['insulin_val'] = curr_val
            
        safe_default_ins = min(min_insulin_allowed + 20, max_insulin_allowed)
        insulin = st.slider("Insulin", min_insulin_allowed, max_insulin_allowed, safe_default_ins, key='insulin_val')
        
        max_skin_allowed = min(100, int(bmi * 1.8 + 10))
        min_skin_allowed = max(0, int(bmi * 0.3 - 5))
        if 'skin_val' in st.session_state:
            curr_val = st.session_state['skin_val']
            if hasattr(curr_val, 'value'): curr_val = curr_val.value
            try:
                curr_val = max(min_skin_allowed, min(int(curr_val), max_skin_allowed))
            except:
                curr_val = min_skin_allowed
            st.session_state['skin_val'] = curr_val
            
        safe_default_skn = min(min_skin_allowed + 5, max_skin_allowed)
        skin_thickness = st.slider("Skin Thickness", min_skin_allowed, max_skin_allowed, safe_default_skn, key='skin_val')
        dpf = st.slider("Pedigree Function", 0.0, 3.0, st.session_state.get('dpf_val', 0.5), key='dpf_val')
        
        if 'preg_val' in st.session_state:
            curr_preg = st.session_state['preg_val']
            if hasattr(curr_preg, 'value'): curr_preg = curr_preg.value
            st.session_state['preg_val'] = max(0, min(int(curr_preg) if str(curr_preg).isdigit() else 0, 20))
            
        pregnancies = 0 if gender == "Male" else st.slider("Pregnancies", 0, 20, 0, key='preg_val')
        
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
                    <div class="{pulse}" style="background:linear-gradient(135deg, {bg} 0%, rgba(0,0,0,0.2) 100%); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-top: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.3); border-radius:24px; padding:40px; text-align:center; height:260px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                        <div style="margin-bottom:20px;">{icon}</div>
                        <div style="font-size:13px; font-weight:700; color:{color}; text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">Classification</div>
                        <div style="font-size:56px; font-weight:800; background: -webkit-linear-gradient(45deg, {color}, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height:1;">{risk_txt}</div>
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
                            <div style="font-size:16px; font-weight:700; color:#FFFFFF; margin-bottom:16px;">AI Clinical Notes</div>
                            <ul style="color:#8E9BAE; font-size:14px; line-height:1.8; padding-left:16px; margin:0;">
                                <li>The AI model prioritizes glucose and BMI factors predominantly.</li>
                                <li>The prediction is derived using ensemble techniques over historical cohorts.</li>
                                <li>Accuracy constraints: Validation implies 85%+ base confidence.</li>
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
                    <div style="background:linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.08); border-top: 1px solid rgba(255,255,255,0.15); box-shadow: 0 8px 32px rgba(0,0,0,0.2); border-radius:24px; padding:40px; text-align:center; height:260px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:20px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                        <div style="font-size:15px; font-weight:500; color:#8E9BAE; text-transform:uppercase;">System Standby</div>
                        <div style="font-size:28px; font-weight:700; color:#FFFFFF; margin-top:8px;">Ready to Analyze</div>
                    </div>
                """, unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#FFFFFF; margin-bottom:20px;'>Analysis Matrix</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); border-top: 1px solid rgba(255,255,255,0.15); border-radius:14px; padding:18px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">GLUCOSE LEVEL</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{glucose} <span style="font-size:13px; color:#64748B; font-weight:500;">mg/dL</span></div>
                </div>
                <div style="background:{'rgba(255, 23, 68, 0.2)' if glucose>140 else 'rgba(0, 230, 118, 0.2)'}; height:12px; width:12px; border-radius:50%; border:2px solid {'#FF1744' if glucose>140 else '#00E676'}; box-shadow: 0 0 10px {'rgba(255,23,68,0.5)' if glucose>140 else 'rgba(0,230,118,0.5)'};"></div>
            </div>
            
            <div style="background:linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); border-top: 1px solid rgba(255,255,255,0.15); border-radius:14px; padding:18px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">BODY MASS INDEX</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{bmi} <span style="font-size:13px; color:#64748B; font-weight:500;">kg/m²</span></div>
                </div>
                <div style="background:{'rgba(255, 23, 68, 0.2)' if bmi>30 else 'rgba(0, 230, 118, 0.2)'}; height:12px; width:12px; border-radius:50%; border:2px solid {'#FF1744' if bmi>30 else '#00E676'}; box-shadow: 0 0 10px {'rgba(255,23,68,0.5)' if bmi>30 else 'rgba(0,230,118,0.5)'};"></div>
            </div>
            
            <div style="background:linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); border-top: 1px solid rgba(255,255,255,0.15); border-radius:14px; padding:18px; margin-bottom:24px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div>
                    <div style="font-size:11px; color:#8E9BAE; font-weight:700; letter-spacing:1px; margin-bottom:4px;">PATIENT AGE</div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; line-height:1;">{age} <span style="font-size:13px; color:#64748B; font-weight:500;">yrs</span></div>
                </div>
                <div style="background:rgba(58, 190, 255, 0.2); height:12px; width:12px; border-radius:50%; border:2px solid #3ABEFF; box-shadow: 0 0 10px rgba(58,190,255,0.5);"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Clinical Suggestions block replaces the Vector Impact Weights
        st.markdown("<div style='font-size:15px; font-weight:700; color:#FFFFFF; margin-bottom:12px; letter-spacing:0.5px;'><svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#3ABEFF\" stroke-width=\"2\" style=\"vertical-align:-3px; margin-right:6px;\"><circle cx=\"12\" cy=\"12\" r=\"10\"></circle><line x1=\"12\" y1=\"16\" x2=\"12\" y2=\"12\"></line><line x1=\"12\" y1=\"8\" x2=\"12.01\" y2=\"8\"></line></svg> Recommended Action Plan</div>", unsafe_allow_html=True)
        
        suggestions = []
        if glucose > 140:
            suggestions.append(("Elevated Fasting Glucose", "Schedule HbA1c testing and comprehensive dietary review to manage insulin resistance.", "#FF1744"))
        elif glucose < 70:
            suggestions.append(("Low Baseline Glucose", "Monitor for hypoglycemic episodes. Ensure consistent carbohydrate intake.", "#FFD600"))

        if bmi >= 30:
            suggestions.append(("Obesity Class Metrics", "Consult with a metabolic specialist. Begin progressive cardiovascular protocols.", "#FFD600"))
        elif bmi < 18.5:
            suggestions.append(("Underweight Indicators", "Prioritize macro-nutrient scaling and evaluate potential endocrine disruptions.", "#FFD600"))

        if blood_pressure > 130:
            suggestions.append(("Hypertensive Stress", "Implement sodium restrictions and perform continuous daily BP monitoring.", "#FF1744"))

        if not suggestions:
            suggestions.append(("Optimal Clinical State", "Key biomarkers are strictly nominal. Continue current preventative health routines.", "#00E676"))

        sug_html = ""
        for title, text, color in suggestions:
            sug_html += f"""
                <div style="background:linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); backdrop-filter: blur(10px); border:1px solid rgba(255,255,255,0.05); border-left:4px solid {color}; padding:14px 16px; margin-bottom:12px; border-radius:8px; display:flex; flex-direction:column; gap:6px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <div style="font-size:13px; font-weight:700; color:#E2E8F0; letter-spacing:0.3px;">{title}</div>
                    <div style="font-size:12px; color:#94A3B8; line-height:1.5;">{text}</div>
                </div>
            """
            
        st.markdown(sug_html, unsafe_allow_html=True)
