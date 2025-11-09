import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Green Meter App", layout="wide")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.title("INPUTS - ACTIVITY DATA")

cars_km = st.sidebar.number_input("Cars - Distance (km/year)", value=250000)
trucks_km = st.sidebar.number_input("Trucks - Distance (km/year)", value=150000)
buses_km = st.sidebar.number_input("Buses - Distance (km/year)", value=80000)
forklifts_hr = st.sidebar.number_input("Forklifts - Operating time (hours/year)", value=2000)
planes_hr = st.sidebar.number_input("Cargo Planes - Flight time (hours/year)", value=400)
lighting_kwh = st.sidebar.number_input("Office Lighting - Electricity (kWh/year)", value=120000)
heating_kwhth = st.sidebar.number_input("Heating - Thermal energy (kWh-th/year)", value=50000)
cooling_kwh = st.sidebar.number_input("Cooling (A/C) - Electricity (kWh/year)", value=300000)
computing_kwh = st.sidebar.number_input("Computing (IT) - Electricity (kWh/year)", value=90000)
subs_ton = st.sidebar.number_input("Subcontractors - Total (tons CO₂e/year)", value=120)

st.sidebar.markdown("---")
st.sidebar.title("ADJUSTMENTS - SLIDERS")
ev_share = st.sidebar.slider("EV Share for Cars (%)", 0, 100, 30)
km_reduction = st.sidebar.slider("KM Reduction for Cars (%)", 0, 100, 10)
load_factor = st.sidebar.slider("Plane Load Factor (%)", 0, 100, 60)

# -----------------------------
# Emission Factors
# -----------------------------
factors = {
    "Cars": 0.18,
    "Trucks": 0.90,
    "Buses": 1.10,
    "Forklifts": 4.0,
    "Planes": 9000,
    "Lighting": 0.42,
    "Heating": 0.20,
    "Cooling": 0.42,
    "Computing": 0.42
}

# -----------------------------
# Calculations
# -----------------------------

# Baseline (no optimization)
baseline = {
    "Cars": (cars_km * factors["Cars"]) / 1000,
    "Trucks": (trucks_km * factors["Trucks"]) / 1000,
    "Buses": (buses_km * factors["Buses"]) / 1000,
    "Forklifts": (forklifts_hr * factors["Forklifts"]) / 1000,
    "Planes": (planes_hr * factors["Planes"] * (load_factor / 100)) / 1000,
    "Lighting": (lighting_kwh * factors["Lighting"]) / 1000,
    "Heating": (heating_kwhth * factors["Heating"]) / 1000,
    "Cooling": (cooling_kwh * factors["Cooling"]) / 1000,
    "Computing": (computing_kwh * factors["Computing"]) / 1000,
    "Subcontractors": subs_ton
}

# Optimized (applying EV share and KM reduction)
optimized_cars = (cars_km * factors["Cars"] *
                 (1 - 0.7 * (ev_share / 100)) *  # EVs emit 70% less
                 (1 - km_reduction / 100)) / 1000

optimized = baseline.copy()
optimized["Cars"] = optimized_cars

# Total Emissions
baseline_total = sum(baseline.values())
optimized_total = sum(optimized.values())

# -----------------------------
# Data for Charts
# -----------------------------
df_baseline = pd.DataFrame({
    "Category": list(baseline.keys()),
    "Emissions": list(baseline.values()),
    "Type": "Baseline"
})

df_optimized = pd.DataFrame({
    "Category": list(optimized.keys()),
    "Emissions": list(optimized.values()),
    "Type": "Optimized"
})

df_all = pd.concat([df_baseline, df_optimized])

# -----------------------------
# Layout
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.title("Green Meter App 🌱")
    st.subheader("Carbon-Aware Logistics Dashboard")

    st.metric("Baseline Total (tons CO₂e)", f"{baseline_total:,.0f}")
    st.metric("Optimized Total (tons CO₂e)", f"{optimized_total:,.0f}")
    st.metric("Reduction (%)", f"{(1 - optimized_total / baseline_total) * 100:.1f}%")

    st.markdown("### Emission Share by Category (Pie - Optimized)")
    fig_pie = px.pie(df_optimized, names="Category", values="Emissions",
                     color_discrete_sequence=px.colors.qualitative.Dark2)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("### Total Emissions (tons CO₂e) — Baseline vs Optimized")
    df_summary = pd.DataFrame({
        "Scenario": ["Baseline", "Optimized"],
        "Emissions": [baseline_total, optimized_total]
    })
    fig_bar = px.bar(df_summary, x="Scenario", y="Emissions", text_auto=True,
                     color="Scenario", color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# Footer Info
# -----------------------------
st.markdown("---")
st.markdown("""
**Assumptions:**
- EVs emit 70% less than gasoline cars.  
- Plane load factor scales aircraft emissions linearly.  
- All emission factors are per the reference table.  
""")