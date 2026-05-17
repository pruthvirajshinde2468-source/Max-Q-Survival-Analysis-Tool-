import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from atmosphere import USStandardAtmosphere1976
from rocket import Rocket
from simulation import Simulation, get_profile_a, get_profile_b, get_profile_c
from analysis import Analysis

# Page Config
st.set_page_config(page_title="Max-Q Survival Analysis Tool", layout="wide")

st.title("🚀 Max-Q Survival Analysis Tool")
st.markdown("""
This tool analyzes the structural loads and performance impact of different throttle strategies during rocket ascent.
Developed for high-fidelity physics-based mission planning.
""")

# --- Sidebar: Rocket Parameters ---
st.sidebar.header("Rocket Physical Parameters")
m_liftoff = st.sidebar.number_input("Total Liftoff Mass (kg)", value=62000)
diameter = st.sidebar.number_input("Rocket Diameter (m)", value=2.0)
max_q_limit = st.sidebar.number_input("Structural Q Limit (Pa)", value=40000)

st.sidebar.header("Throttle Strategy Settings")
transonic_start = st.sidebar.slider("Transonic Start (Mach)", 0.5, 1.0, 0.8)
transonic_end = st.sidebar.slider("Transonic End (Mach)", 1.0, 2.0, 1.5)
custom_throttle = st.sidebar.slider("Custom Profile Throttle (%)", 10, 100, 60)

# --- Wind Profile Selection ---
st.sidebar.header("Atmospheric Disturbance")
wind_enabled = st.sidebar.checkbox("Enable Wind Effects", value=True)
jet_stream_speed = st.sidebar.slider("Jet Stream Max Speed (m/s)", 0, 100, 40)

def wind_profile(y):
    if not wind_enabled: return 0.0
    # Jet stream between 9km and 14km
    if 9000 <= y <= 14000:
        return jet_stream_speed
    return 0.0

# --- Define Profiles ---
def get_custom_profile(t, y, v, mach):
    if transonic_start <= mach <= transonic_end:
        return custom_throttle / 100.0
    return 1.0

# --- Run Simulations ---
@st.cache_data
def run_all_sims(_rocket, _wind_func, _custom_throttle_val):
    sim = Simulation(_rocket)
    
    # Profiles
    profiles = {
        "Profile A (Full)": get_profile_a,
        "Profile B (70%)": get_profile_b,
        "Profile C (50%)": get_profile_c,
        "Profile D (Custom)": lambda t, y, v, mach: (custom_throttle/100.0 if transonic_start <= mach <= transonic_end else 1.0)
    }
    
    all_results = {}
    for name, func in profiles.items():
        all_results[name] = sim.run(func, _wind_func)
        
    return all_results

rocket = Rocket()
# Update rocket with sidebar values
rocket.limit_q = max_q_limit
rocket.diameter = diameter
rocket.ref_area = np.pi * (diameter / 2)**2

results_map = run_all_sims(rocket, wind_profile, custom_throttle)

# --- Analysis & Tables ---
st.header("📊 Trajectory Comparison")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Performance Metrics")
    summary_data = []
    limits = {'q': max_q_limit}
    
    baseline_name = "Profile A (Full)"
    baseline_summary = Analysis.get_summary(results_map[baseline_name], limits)
    
    for name, res in results_map.items():
        summary = Analysis.get_summary(res, limits)
        penalties = Analysis.calculate_penalties(baseline_summary, summary, rocket.s1_vac_isp)
        
        status = "✅ Safe" if summary['min_margin_q'] > 0 else "❌ Exceeded"
        color = "green" if status == "✅ Safe" else "red"
        
        summary_data.append({
            "Profile": name,
            "Max Q (Pa)": f"{summary['max_q']:,.0f}",
            "Min Safety Margin": f"{summary['min_margin_q']*100:.1f}%",
            "Final Velocity (m/s)": f"{summary['final_v']:,.0f}",
            "Payload Penalty (kg)": f"{penalties['payload_penalty_kg']:.1f}",
            "Status": status
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)

with col2:
    st.subheader("Atmosphere Profile")
    alt_range = np.linspace(0, 150000, 200)
    atm_data = [USStandardAtmosphere1976.get_properties(z) for z in alt_range]
    df_atm = pd.DataFrame(atm_data, columns=['Temp', 'Press', 'Rho', 'SoundSpeed'])
    df_atm['Alt'] = alt_range / 1000
    
    fig_atm, ax_atm = plt.subplots(figsize=(6, 4))
    ax_atm.plot(df_atm['Rho'], df_atm['Alt'], label='Density (kg/m3)')
    ax_atm.set_ylabel("Altitude (km)")
    ax_atm.set_xlabel("Density")
    ax_atm.grid(True, alpha=0.3)
    st.pyplot(fig_atm)

# --- Plots ---
st.header("📈 Flight Dynamic Plots")
plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    fig_q, ax_q = plt.subplots()
    for name, res in results_map.items():
        df = pd.DataFrame(res)
        ax_q.plot(df['altitude']/1000, df['q'], label=name)
    ax_q.axhline(max_q_limit, color='red', linestyle='--', label='Limit')
    ax_q.set_xlabel("Altitude (km)")
    ax_q.set_ylabel("Dynamic Pressure Q (Pa)")
    ax_q.legend()
    ax_q.grid(True)
    st.pyplot(fig_q)

with plot_col2:
    fig_mach, ax_mach = plt.subplots()
    for name, res in results_map.items():
        df = pd.DataFrame(res)
        ax_mach.plot(df['time'], df['mach'], label=name)
    ax_mach.set_xlabel("Time (s)")
    ax_mach.set_ylabel("Mach Number")
    ax_mach.legend()
    ax_mach.grid(True)
    st.pyplot(fig_mach)

st.header("🛡️ Structural Load Analysis")
fig_load, ax_load = plt.subplots(figsize=(10, 4))
for name, res in results_map.items():
    df = pd.DataFrame(res)
    # Combined load factor (simplified)
    load_factor = df['axial_g'] + (df['side_load'] / 1e4) # Normalized side load
    ax_load.plot(df['altitude']/1000, load_factor, label=name)
ax_load.set_xlabel("Altitude (km)")
ax_load.set_ylabel("Combined Load Factor")
ax_load.legend()
ax_load.grid(True)
st.pyplot(fig_load)

# --- Recommendations ---
st.header("💡 Engineering Recommendations")
best_profile = "None"
min_safe_penalty = float('inf')

for name, res in results_map.items():
    summary = Analysis.get_summary(res, limits)
    penalties = Analysis.calculate_penalties(baseline_summary, summary, rocket.s1_vac_isp)
    if summary['min_margin_q'] > 0.1: # 10% safety buffer
        if penalties['payload_penalty_kg'] < min_safe_penalty:
            min_safe_penalty = penalties['payload_penalty_kg']
            best_profile = name

if best_profile != "None":
    st.success(f"**Recommended Strategy:** {best_profile}. This profile maintains a >10% structural safety margin while minimizing payload penalty ({min_safe_penalty:.1f} kg).")
else:
    st.error("⚠️ All current profiles exceed structural limits or buffer. Consider further throttling down or redesigning structure.")

# Download Report Button
if st.button("Generate Complete PDF Report"):
    import report_gen
    
    # Prepare summary table for PDF (remove status emoji for PDF compatibility if needed, or keep)
    pdf_summary = []
    for row in summary_data:
        pdf_summary.append({
            "Profile": row["Profile"],
            "Max Q (Pa)": row["Max Q (Pa)"],
            "Min Safety Margin": row["Min Safety Margin"],
            "Final Velocity (m/s)": row["Final Velocity (m/s)"],
            "Payload Penalty (kg)": row["Payload Penalty (kg)"],
            "Status": row["Status"].replace("✅ ", "").replace("❌ ", "")
        })
    
    output_pdf = "MaxQ_Analysis_Report.pdf"
    report_gen.generate_pdf(results_map, rocket, pdf_summary, best_profile, output_pdf)
    
    with open(output_pdf, "rb") as f:
        st.download_button(
            label="Download PDF Report",
            data=f,
            file_name=output_pdf,
            mime="application/pdf"
        )
    st.success(f"Report generated successfully: {output_pdf}")
