# Max-Q Survival Analysis Tool 🚀

A high-fidelity physics-based simulation and analysis tool designed to evaluate rocket structural safety and performance trade-offs during ascent. This tool focuses on **Max-Q** (Maximum Dynamic Pressure), providing interactive analysis of throttle strategies, structural loads, and atmospheric disturbances.

## 🌟 Key Features

- **US Standard Atmosphere 1976**: Full atmospheric model from 0 to 150 km.
- **Rocket Dynamics Engine**: 2D trajectory simulation with mass variation and CG/CP shifting.
- **Aerodynamic Modeling**: Mach-dependent $C_d$ calculations with transonic wave drag modeling.
- **Structural Load Analysis**: Real-time calculation of axial compression, bending moments, and safety margins.
- **Throttle Strategy Optimizer**: Compare multiple profiles to find the optimal balance between performance and safety.
- **Wind & Disturbance Modeling**: Integration of jet stream effects and wind shear on structural stability.
- **Interactive Dashboard**: Streamlit-based UI for real-time mission planning.
- **Automated Reporting**: Single-click PDF report generation with embedded charts and engineering recommendations.

## 🛠️ Tech Stack

- **Core**: Python 3.x
- **Analysis**: NumPy, SciPy, Pandas
- **Visualization**: Matplotlib, Plotly, Streamlit
- **Reporting**: fpdf2

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed. It is recommended to use a virtual environment.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/max-q-survival-analysis.git
   cd max-q-survival-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Tool

Launch the interactive dashboard:
```bash
streamlit run app.py
```

## 📊 Analysis Workflow

1. **Atmosphere Model**: Validated against NOAA USSA 1976 data.
2. **Rocket Physics**: Configure liftoff mass, diameter, and engine thrust in the sidebar.
3. **Simulation**: The engine runs a 2D trajectory through the atmosphere.
4. **Max-Q Identification**: The tool automatically flags the peak dynamic pressure point.
5. **Report Generation**: Click "Generate Complete PDF Report" to export a professional analysis document.

## 🛡️ Structural Safety Limits

The tool monitors three critical safety parameters:
- **Maximum Dynamic Pressure ($Q$)**: Design limit for the fairing and primary structure.
- **Axial Load (G-force)**: Compressive limits for the propellant tanks.
- **Bending Moment**: Side loads caused by Wind + Angle of Attack ($\alpha$) during transonic flight.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed for advanced mission analysis and rocket structural engineering.*
