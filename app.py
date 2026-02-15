import streamlit as st
import openmdao.api as om
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Design Optimizer",
    page_icon="✈️",
    layout="wide"
)

# --- PHYSICS MODELS ---
class ThermalComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('windshield_size', val=2.5)
        self.add_output('heat_load', val=4.0)

    def compute(self, inputs, outputs):
        outputs['heat_load'] = (1.1 * inputs['windshield_size']) + 1.5

class CoolingSystemComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('heat_load', val=4.0)
        self.add_output('system_weight', val=100.0)

    def compute(self, inputs, outputs):
        outputs['system_weight'] = (22.0 * inputs['heat_load']) + 30.0

class FuelComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('system_weight', val=100.0)
        self.add_input('windshield_size', val=2.5) 
        self.add_output('fuel_burn', val=150.0)

    def compute(self, inputs, outputs):
        weight_penalty = 0.05 * inputs['system_weight']
        drag_penalty = 8.0 * (inputs['windshield_size']**1.2)
        outputs['fuel_burn'] = weight_penalty + drag_penalty

class AirplaneCascade(om.Group):
    def setup(self):
        self.add_subsystem('thermal', ThermalComponent(), promotes=['windshield_size'])
        self.add_subsystem('cooling', CoolingSystemComponent())
        self.add_subsystem('perf', FuelComponent(), promotes=['fuel_burn', 'windshield_size'])
        self.connect('thermal.heat_load', 'cooling.heat_load')
        self.connect('cooling.system_weight', 'perf.system_weight')

def run_model(windshield_size):
    prob = om.Problem()
    prob.model = AirplaneCascade()
    prob.setup()
    prob.set_val('windshield_size', windshield_size)
    prob.run_model()
    return {
        'windshield_size': prob.get_val('windshield_size')[0],
        'heat_load': prob.get_val('thermal.heat_load')[0],
        'system_weight': prob.get_val('cooling.system_weight')[0],
        'fuel_burn': prob.get_val('fuel_burn')[0]
    }

def create_windshield_viz(area):
    """
    Realistic aircraft cockpit windshield visualization.
    Area controls overall size.
    """

    # --- Scale geometry from area ---
    width = np.sqrt(area * 2.2)       # lateral span
    height = area / width             # vertical size
    depth = width * 0.6               # curvature depth

    # Surface resolution
    u = np.linspace(-1, 1, 30)
    v = np.linspace(0, 1, 20)
    U, V = np.meshgrid(u, v)

    # --- Curved windshield surface ---
    # Elliptical wrap + backward rake
    X = depth * (1 - V**1.5)           # backward rake
    Y = (width / 2) * U * (1 - 0.3*V)  # taper towards top
    Z = height * V**1.2                # curved vertical rise

    fig = go.Figure()

    # Windshield glass
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, "rgba(135,206,235,0.9)"],
                    [1, "rgba(180,220,255,0.9)"]],
        showscale=False,
        name="Windshield"
    ))

    # --- Cockpit frame outline ---
    frame_u = np.linspace(-1, 1, 50)
    frame_x = np.zeros_like(frame_u)
    frame_y = (width / 2) * frame_u
    frame_z = np.zeros_like(frame_u)

    fig.add_trace(go.Scatter3d(
        x=frame_x,
        y=frame_y,
        z=frame_z,
        mode="lines",
        line=dict(color="black", width=6),
        showlegend=False
    ))

    # --- Nose hint (for realism) ---
    nose_theta = np.linspace(-np.pi/2, np.pi/2, 40)
    nose_x = -0.15 * np.cos(nose_theta)
    nose_y = (width / 2) * np.sin(nose_theta)
    nose_z = -0.15 * np.ones_like(nose_theta)

    fig.add_trace(go.Scatter3d(
        x=nose_x,
        y=nose_y,
        z=nose_z,
        mode="lines",
        line=dict(color="gray", width=3),
        showlegend=False
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=1.2, z=0.8)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=350
    )

    return fig


# --- STREAMLIT UI ---
st.title("Design Cascade Optimizer")

with st.sidebar:
    st.header("⚙️ Parameters")
    windshield_size = st.slider("Windshield Area (m²)", 1.0, 10.0, 3.6, 0.1)
    run_button = st.button("Update Analysis", type="primary", use_container_width=True)

# Run logic
res = run_model(windshield_size)

# 1. Geometry Visualization Section
col_left, col_right = st.columns([1, 1.5])
with col_left:
    st.subheader("Design Geometry")
    st.write(f"Current Area: **{windshield_size} m²**")
    st.plotly_chart(create_windshield_viz(windshield_size), use_container_width=True)

with col_right:
    st.subheader("Regulatory Compliance")
    fuel = res['fuel_burn']
    st.write(f"Evaluating limits based on Mission Fuel Burn: **{fuel:.1f} kg**")
    
    # Logic for compliances based on fuel burn thresholds
    def get_status_mark(violated):
        return "❌" if violated else "✅"
    
    icao_violated = fuel > 64.4
    corsia_violated = fuel > 102.0
    faa_violated = fuel > 79.1
    easa_violated = fuel > 102.0
    
    st.markdown(f"**{get_status_mark(icao_violated)} ICAO CO₂ Emissions Standard for Aeroplanes**")
    st.markdown(f"**{get_status_mark(corsia_violated)} CORSIA**")
    st.markdown(f"**{get_status_mark(faa_violated)} FAA, 14 CFR Part 34**")
    st.markdown(f"**{get_status_mark(easa_violated)} EASA, CS-34**")
    
    if icao_violated or corsia_violated or faa_violated or easa_violated:
        st.error("Warning: One or more emissions compliance standards are currently violated due to excessive fuel burn.")
    else:
        st.success("All listed emissions standards are currently satisfied.")

# 2. Centered Metrics Section
st.divider()
st.subheader("System Dependency Cascade")

# Custom CSS to perfectly center the arrow vertically and horizontally
st.markdown("""
    <style>
    .centered-arrow-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100px;
    }
    .arrow-text {
        font-size: 30px;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

m1, a1, m2, a2, m3, a3, m4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])

with m1:
    st.metric("Windshield Area (m²)", f"{res['windshield_size']:.1f}")
    st.caption("Initial Design Choice")
with a1:
    st.markdown('<div class="centered-arrow-container"><span class="arrow-text">➡️</span></div>', unsafe_allow_html=True)
with m2:
    st.metric("Cabin Heat Load (kW)", f"{res['heat_load']:.1f}")
    st.caption("Thermal Impact")
with a2:
    st.markdown('<div class="centered-arrow-container"><span class="arrow-text">➡️</span></div>', unsafe_allow_html=True)
with m3:
    st.metric("Cooling Sys Weight (kg)", f"{res['system_weight']:.1f}")
    st.caption("Structural Impact")
with a3:
    st.markdown('<div class="centered-arrow-container"><span class="arrow-text">➡️</span></div>', unsafe_allow_html=True)
with m4:
    st.metric("Mission Fuel Burn (kg)", f"{res['fuel_burn']:.1f}")
    st.caption("Final Performance Cost")

# 3. Data Trends
st.divider()
st.subheader("Performance Impact")
fig_trend = go.Figure()
stages = ['Windshield Area', 'Heat Load', 'System Weight', 'Fuel Burn']
values = [res['windshield_size'], res['heat_load'], res['system_weight'], res['fuel_burn']]
fig_trend.add_trace(go.Scatter(x=stages, y=values, mode='lines+markers+text', text=[f'{v:.1f}' for v in values], textposition='top center'))
fig_trend.update_layout(height=400)
st.plotly_chart(fig_trend, use_container_width=True)