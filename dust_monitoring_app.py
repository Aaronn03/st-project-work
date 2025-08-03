import streamlit as st
import pandas as pd
import numpy as np

# === Dust Suppression Controller ===
class DustSuppressionController:
    """
    Implements automated dust suppression based on PM level.
    Returns a dictionary with suppression details.
    """
    def __init__(self, threshold_pm=50.0):
        self.threshold_pm = threshold_pm
        self.suppression_history = []

    def evaluate_and_control(self, predicted_pm, timestamp=None):
        """
        Evaluate dust level and activate suppression if needed.
        Returns a dictionary with action details.
        """
        # Default values
        level = "LOW"
        action = "NONE"
        intensity = 0.0
        duration = 0
        water_usage = 0.0
        energy = 0.0

        if predicted_pm > self.threshold_pm * 0.95:
            if predicted_pm > self.threshold_pm:
                level = "HIGH"
                intensity = 1.0
                duration = 30  # minutes
            else:
                level = "MEDIUM"
                intensity = 0.6
                duration = 15  # minutes

            action = "ACTIVATE"
            # Example calculations (customize as needed)
            water_usage = intensity * duration * 10  # liters
            energy = intensity * duration * 0.5      # kWh

        # Prepare result dictionary
        result = {
            'timestamp': timestamp or 'now',
            'predicted_pm': predicted_pm,
            'level': level,
            'intensity': intensity,
            'duration': duration,
            'action': action,
            'water_usage': water_usage,
            'energy': energy
        }

        # Log action if suppression is activated
        if action == "ACTIVATE":
            self.suppression_history.append(result)

        return result

# === Streamlit App ===
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
                result = self.controller.evaluate_and_control(pm)
                results.append((pm, result))
                progress_bar.progress((i + 1) / samples)
                
            # Display all results
            st.subheader("Simulation Results")
            for pm, result in results:
                with st.expander(f"PM: {pm} µg/m³ - {result['level']}"):
                    self._show_result_details(pm, result)
    
    def _display_results(self, pm_level):
        """Display results for manual demo"""
        result = self.controller.evaluate_and_control(pm_level)
        
        st.metric("Current PM Level", f"{pm_level} µg/m³")
        st.metric("Dust Level", result['level'])
        
        if result['action'] == 'ACTIVATE':
            st.warning("Suppression Activated!")
            cols = st.columns(4)
            cols[0].metric("Intensity", f"{result['intensity'] * 100:.0f}%")
            cols[1].metric("Duration", f"{result['duration']} mins")
            cols[2].metric("Water", f"{result.get('water_usage', 0):.1f}L")
            cols[3].metric("Energy", f"{result.get('energy', 0):.1f}kWh")
        else:
            st.success("No suppression needed - Safe levels")
    
    def _show_result_details(self, pm_level, result):
        """Show detailed results for auto demo"""
        st.metric("Current PM Level", f"{pm_level} µg/m³")
        st.metric("Dust Level", result['level'])
        
        if result['action'] == 'ACTIVATE':
            st.warning("Suppression Activated!")
            st.write("### Suppression Details")
            st.json(result)
        else:
            st.success("No suppression needed - Safe levels")
    
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
    st.set_page_config(
        page_title="Dust Monitoring System",
        page_icon="🌫️",
        layout="wide"
    )
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