import sys

def get_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

app_py = get_file('app.py')
new_compare = get_file('new_compare.py')
new_code = get_file('new_code.py')

# Extract load_* functions and imports from app_py
start_idx = app_py.find('import streamlit')
end_idx = app_py.find('def model_comparison_page():')
header = app_py[start_idx:end_idx].strip() + '\n\n\n'

# Get new_compare
model_comp_code = new_compare.strip() + '\n\n\n'

# Fix new_code to include plotly
plotly_block = '''
                st.markdown("<div style='font-size:16px; font-weight:700; color:#FFFFFF; margin-bottom:16px;'>Prediction Trend Analysis</div>", unsafe_allow_html=True)
                if len(st.session_state.history) > 1:
                    try:
                        import plotly.graph_objects as go
                        hist_rev = list(reversed(st.session_state.history))
                        x_vals = [h[0] for h in hist_rev]
                        y_vals = [float(h[1].strip('%')) for h in hist_rev]
                        marker_colors = [h[3] for h in hist_rev]
                        
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=x_vals, y=y_vals, mode='lines+markers',
                            line=dict(color='#5E81AC', width=2, shape='spline'),
                            marker=dict(color=marker_colors, size=12, line=dict(color='#0B0F14', width=2))
                        ))
                        fig_trend.update_layout(
                            height=180, margin=dict(l=0, r=0, t=5, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            yaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.05)', ticksuffix='%', tickfont=dict(color='#8E9BAE', size=11)),
                            xaxis=dict(tickfont=dict(color='#8E9BAE', size=11), showgrid=False)
                        )
                        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
                    except Exception:
                        pass
                else:
                    st.markdown("<div style='font-size:13px; color:#8E9BAE; padding-bottom:10px;'>Generate at least two predictions to view your historical trend graph.</div>", unsafe_allow_html=True)
'''

# Find insertion point in new_code
ins_marker = 'history_html = "".join(['
parts = new_code.split(ins_marker)
health_dashboard_code = parts[0] + plotly_block + '\n                ' + ins_marker + parts[1]

# Append the main function
footer = '''

def main():
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Health Dashboard", "Model Comparison"],
        label_visibility="collapsed"
    )

    if page == "Health Dashboard":
        health_dashboard_page()
    else:
        model_comparison_page()


if __name__ == "__main__":
    main()
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(header + model_comp_code + health_dashboard_code + footer)
print('Done!')
