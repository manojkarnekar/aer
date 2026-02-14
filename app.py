import streamlit as st
import openmdao.api as om
import plotly.graph_objects as go
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Airplane Design Optimizer",
    page_icon="✈️",
    layout="wide"
)

# 1. Define the Thermal Model (Physics or ML Surrogate)
class ThermalComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('windshield_size', val=1.0)
        self.add_output('heat_load', val=1.0)

    def compute(self, inputs, outputs):
        # Simple physics: Heat scales linearly with size
        # In real life, replace this line with a Neural Network prediction
        outputs['heat_load'] = 2.5 * inputs['windshield_size'] + 10

# 2. Define the Weight/Cooling Model
class CoolingSystemComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('heat_load', val=1.0)
        self.add_output('system_weight', val=1.0)

    def compute(self, inputs, outputs):
        # The cooling system weight depends on the heat load
        outputs['system_weight'] = 0.5 * inputs['heat_load'] + 50

# 3. Define the Performance Model (Fuel Consumption)
class FuelComponent(om.ExplicitComponent):
    def setup(self):
        self.add_input('system_weight', val=1.0)
        self.add_input('windshield_size', val=1.0) # Drag also increases with size
        self.add_output('fuel_burn', val=1.0)

    def compute(self, inputs, outputs):
        # Fuel burn increases with both Weight and Drag (size)
        weight_penalty = 0.8 * inputs['system_weight']
        drag_penalty = 1.2 * inputs['windshield_size']
        outputs['fuel_burn'] = weight_penalty + drag_penalty

# 4. Build the Group (The "Cascade")
class AirplaneCascade(om.Group):
    def setup(self):
        # Add the subsystems
        self.add_subsystem('thermal', ThermalComponent(), promotes=['windshield_size'])
        self.add_subsystem('cooling', CoolingSystemComponent())
        self.add_subsystem('perf', FuelComponent(), promotes=['fuel_burn', 'windshield_size'])

        # Connect the cascade: Thermal -> Cooling -> Performance
        self.connect('thermal.heat_load', 'cooling.heat_load')
        self.connect('cooling.system_weight', 'perf.system_weight')

def run_model(windshield_size):
    """Run the OpenMDAO model with given parameters"""
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

def run_parametric_sweep(min_size, max_size, num_points):
    """Run model over a range of windshield sizes"""
    sizes = [min_size + (max_size - min_size) * i / (num_points - 1) for i in range(num_points)]
    results = []
    
    for size in sizes:
        result = run_model(size)
        results.append(result)
    
    return pd.DataFrame(results)

# Streamlit UI
st.title("✈️ Airplane Design Cascade Optimizer")
st.markdown("### Interactive Model for Windshield Sizing")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Model Parameters")
    
    mode = st.radio("Analysis Mode", ["Single Point", "Parametric Sweep"])
    
    if mode == "Single Point":
        windshield_size = st.slider(
            "Windshield Size",
            min_value=0.5,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Size of the windshield (arbitrary units)"
        )
    else:
        st.subheader("Sweep Range")
        min_size = st.number_input("Minimum Size", value=0.5, min_value=0.1, max_value=5.0)
        max_size = st.number_input("Maximum Size", value=10.0, min_value=min_size + 0.1, max_value=15.0)
        num_points = st.slider("Number of Points", min_value=5, max_value=50, value=20)
    
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# Main content
if mode == "Single Point":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Analysis Results")
        
        if run_button or 'last_size' not in st.session_state:
            with st.spinner("Running model..."):
                results = run_model(windshield_size)
                st.session_state.last_results = results
                st.session_state.last_size = windshield_size
        
        if 'last_results' in st.session_state:
            results = st.session_state.last_results
            
            # Display results in metrics
            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric("Windshield Size", f"{results['windshield_size']:.2f}")
            with metric_cols[1]:
                st.metric("Heat Load", f"{results['heat_load']:.2f}")
            with metric_cols[2]:
                st.metric("System Weight", f"{results['system_weight']:.2f}")
            with metric_cols[3]:
                st.metric("Fuel Burn", f"{results['fuel_burn']:.2f}")
            
            # Flow diagram
            st.subheader("🔄 Design Cascade Flow")
            fig = go.Figure()
            
            stages = ['Windshield\nSize', 'Heat\nLoad', 'System\nWeight', 'Fuel\nBurn']
            values = [
                results['windshield_size'],
                results['heat_load'],
                results['system_weight'],
                results['fuel_burn']
            ]
            
            fig.add_trace(go.Scatter(
                x=list(range(len(stages))),
                y=values,
                mode='lines+markers+text',
                marker=dict(size=15, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']),
                line=dict(width=3, color='#95E1D3'),
                text=[f'{v:.2f}' for v in values],
                textposition='top center',
                textfont=dict(size=15, color='#2C3E50')
            ))
            
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(stages))),
                    ticktext=stages,
                    tickfont=dict(size=14)
                ),
                yaxis_title="Value",
                height=500,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

else:  # Parametric Sweep
    st.subheader("📈 Parametric Sweep Analysis")
    
    if run_button or 'sweep_data' not in st.session_state:
        with st.spinner("Running parametric sweep..."):
            df = run_parametric_sweep(min_size, max_size, num_points)
            st.session_state.sweep_data = df
    
    if 'sweep_data' in st.session_state:
        df = st.session_state.sweep_data
        
        # Create plots
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['windshield_size'],
            y=df['heat_load'],
            mode='lines+markers',
            name='Heat Load',
            line=dict(width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['windshield_size'],
            y=df['system_weight'],
            mode='lines+markers',
            name='System Weight',
            line=dict(width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['windshield_size'],
            y=df['fuel_burn'],
            mode='lines+markers',
            name='Fuel Burn',
            line=dict(width=2)
        ))
        
        fig.update_layout(
            xaxis_title="Windshield Size",
            yaxis_title="Value",
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("📋 View Data Table"):
            st.dataframe(
                df.style.format("{:.3f}"),
                use_container_width=True,
                hide_index=True
            )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="airplane_cascade_results.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")