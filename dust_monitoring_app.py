import streamlit as st
import pandas as pd
import numpy as np
import random
from pathlib import Path
from dust_monitoring_fl import DustSuppressionController

# Set page config
st.set_page_config(
    page_title="Dust Monitoring System",
    page_icon="🌫️",
    layout="wide"
)

class DustMonitoringApp:
    def __init__(self):
        self.controller = DustSuppressionController(threshold_pm=50.0)
        
    def manual_demo(self):
        """Manual PM input demo"""
        st.subheader("Manual Suppression Demo")
        
        col1, col2 = st.columns(2)
        pm_level = col1.number_input(
            "Enter PM level (µg/m³)", 
            min_value=0.0,
            max_value=500.0,
            value=30.0,
            step=1.0
        )
        
        if col2.button("Evaluate", key="manual_eval"):
            self._display_results(pm_level)
    
    def auto_demo(self):
        """Automatic random PM demo"""
        st.subheader("Automatic Suppression Demo")
        
        samples = st.slider(
            "Number of samples", 
            min_value=1,
            max_value=20,
            value=5
        )
        
        if st.button("Run Simulation"):
            st.info(f"Testing with {samples} random PM levels...")
            
            # Generate realistic PM values (skewed toward lower values)
            pm_levels = np.clip(
                np.random.exponential(scale=30, size=samples),
                5, 200
            ).round(1)
            
            progress_bar = st.progress(0)
            results = []
            
            for i, pm in enumerate(pm_levels):
                result = self._get_suppression_result(pm)
                results.append((pm, result))
                progress_bar.progress((i + 1) / samples)
                
            # Display all results
            st.subheader("Simulation Results")
            for pm, result in results:
                with st.expander(f"PM: {pm} µg/m³ - {result['level']}"):
                    self._show_result_details(pm, result)
    
    def _get_suppression_result(self, pm_level):
        """Get suppression results for a given PM level"""
        needs_suppression, dust_level = self.controller.evaluate_dust_level(pm_level)
        
        if needs_suppression:
            result = self.controller.activate_suppression(dust_level)
            result['level'] = dust_level
            return result
        return {'level': 'LOW', 'status': 'No suppression needed'}
    
    def _display_results(self, pm_level):
        """Display results for manual demo"""
        result = self._get_suppression_result(pm_level)
        
        st.metric("Current PM Level", f"{pm_level} µg/m³")
        st.metric("Dust Level", result['level'])
        
        if result['status'] != 'No suppression needed':
            st.warning("Suppression Activated!")
            cols = st.columns(4)
            cols[0].metric("Intensity", f"{result['intensity'] * 100:.0f}%")
            cols[1].metric("Duration", f"{result['duration']} mins")
            cols[2].metric("Water", f"{result['resource_usage']['water']:.1f}L")
            cols[3].metric("Energy", f"{result['resource_usage']['energy']:.1f}kWh")
        else:
            st.success("No suppression needed - Safe levels")
    
    def _show_result_details(self, pm_level, result):
        """Show detailed results for auto demo"""
        self._display_results(pm_level)
        
        if result['status'] != 'No suppression needed':
            st.write("### Suppression Details")
            st.json(result)
    
    def data_analysis(self, data_path):
        """Dataset analysis section"""
        st.subheader("Dataset Analysis")
        
        try:
            df = pd.read_csv(data_path)
            
            st.write("#### Dataset Overview")
            st.dataframe(df.head())
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("##### Basic Statistics")
                st.dataframe(df.describe())
                
            with col2:
                if 'PM' in df.columns:
                    st.write("##### PM Analysis")
                    exceedances = (df['PM'] > 50).mean() * 100
                    st.metric("Threshold Exceedances", f"{exceedances:.1f}% > 50 µg/m³")
                    
                    hist_values = np.histogram(df['PM'], bins=20, range=(0, 200))[0]
                    st.bar_chart(hist_values)
                    
        except Exception as e:
            st.error(f"Error loading dataset: {e}")

def main():
    st.title("🌫️ Dust Monitoring System")
    st.markdown("""
    *Application of Machine Learning in Dust Monitoring and Suppression*
    """)
    
    app = DustMonitoringApp()
    data_path = r"C:\Users\HP\Documents\Nana\Project 2\filtered_csv.csv"
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["Dataset Analysis", "Manual Demo", "Automatic Demo"]
    )
    
    if menu == "Dataset Analysis":
        app.data_analysis(data_path)
    elif menu == "Manual Demo":
        app.manual_demo()
    elif menu == "Automatic Demo":
        app.auto_demo()

if __name__ == "__main__":
    main()