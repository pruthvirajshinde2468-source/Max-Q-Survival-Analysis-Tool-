from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import datetime

class MaxQReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Max-Q Survival Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_pdf(results_map, rocket, summary_table, recommendations, output_path="MaxQ_Analysis_Report.pdf"):
    pdf = MaxQReport()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. Executive Summary', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"This report provides a detailed structural and performance analysis of the rocket ascent under various throttle strategies. "
                         f"The goal is to identify the optimal balance between Max-Q structural safety and payload delivery performance. "
                         f"Recommended strategy: {recommendations}")
    pdf.ln(5)
    
    # 2. Rocket Parameters
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. Rocket Physical Parameters', 0, 1)
    pdf.set_font('Arial', '', 10)
    params = [
        f"Total Liftoff Mass: {rocket.m_s1_prop + rocket.m_s1_dry + rocket.m_s2_prop + rocket.m_s2_dry + rocket.m_payload:,.0f} kg",
        f"Rocket Diameter: {rocket.diameter} m",
        f"Reference Area: {rocket.ref_area:.2f} m^2",
        f"Stage 1 SL Thrust: {rocket.s1_sl_thrust/1e6:.2f} MN",
        f"Design Q Limit: {rocket.limit_q:,.0f} Pa"
    ]
    for p in params:
        pdf.cell(0, 5, f"- {p}", 0, 1)
    pdf.ln(5)
    
    # 3. Comparison Table
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. Performance and Safety Summary', 0, 1)
    
    # Table Header
    pdf.set_font('Arial', 'B', 9)
    col_width = [40, 30, 30, 30, 30, 30]
    headers = ["Profile", "Max Q (Pa)", "Margin", "Final V", "Penalty (kg)", "Status"]
    for i, h in enumerate(headers):
        pdf.cell(col_width[i], 10, h, 1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font('Arial', '', 8)
    for row in summary_table:
        pdf.cell(col_width[0], 8, str(row['Profile']), 1)
        pdf.cell(col_width[1], 8, str(row['Max Q (Pa)']), 1)
        pdf.cell(col_width[2], 8, str(row['Min Safety Margin']), 1)
        pdf.cell(col_width[3], 8, str(row['Final Velocity (m/s)']), 1)
        pdf.cell(col_width[4], 8, str(row['Payload Penalty (kg)']), 1)
        pdf.cell(col_width[5], 8, str(row['Status']), 1)
        pdf.ln()
    pdf.ln(10)
    
    # 4. Plots
    # Generate and save temporary plots
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '4. Flight Dynamic Visualization', 0, 1)
    
    # Plot 1: Q vs Altitude
    plt.figure(figsize=(6, 4))
    for name, res in results_map.items():
        plt.plot([r['altitude']/1000 for r in res], [r['q'] for r in res], label=name)
    plt.axhline(rocket.limit_q, color='r', linestyle='--')
    plt.xlabel("Altitude (km)")
    plt.ylabel("Q (Pa)")
    plt.legend(prop={'size': 6})
    plt.grid(True)
    plt.savefig("tmp_q_plot.png")
    pdf.image("tmp_q_plot.png", x=10, w=180)
    plt.close()
    
    pdf.add_page()
    # Plot 2: Mach vs Time
    plt.figure(figsize=(6, 4))
    for name, res in results_map.items():
        plt.plot([r['time'] for r in res], [r['mach'] for r in res], label=name)
    plt.xlabel("Time (s)")
    plt.ylabel("Mach")
    plt.legend(prop={'size': 6})
    plt.grid(True)
    plt.savefig("tmp_mach_plot.png")
    pdf.image("tmp_mach_plot.png", x=10, w=180)
    plt.close()

    # Cleanup
    if os.path.exists("tmp_q_plot.png"): os.remove("tmp_q_plot.png")
    if os.path.exists("tmp_mach_plot.png"): os.remove("tmp_mach_plot.png")
    
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    # Test generation with dummy data if needed
    print("Report generator module loaded.")
