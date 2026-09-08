import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = BASE_DIR / "documents" / "sample_reports"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

REPORTS = [
    {
        "filename": "demo_well_W001_DDR.pdf",
        "title": "DAILY DRILLING REPORT - DEMO WELL W001",
        "lines": [
            "================================================================================",
            "DEMO SYNTHETIC DRILLING DATA - OIL INDIA LIMITED HACKATHON PROTOTYPE",
            "================================================================================",
            "Well Name: DEMO-W001 (Offset South)",
            "Field: Dikom / Greater Dibrugarh Area",
            "Date: 2024-03-15 | Report Number: DDR-42 | Rig: Synthetic-Rig-01",
            "Depth: 3420.0 m (MD) | Formation: Barail Sandstone",
            "--------------------------------------------------------------------------------",
            "OPERATIONAL SUMMARY & INCIDENT DETAILS:",
            "Event: MUD_LOSS (Lost Circulation Incident)",
            "Severity: HIGH",
            "Observed Symptoms: Sudden drop in pit volume (-28 bbls/hr) and standpipe pressure drop (180 psi).",
            "Cause: Intersected high-permeability thief zone / micro-fracture corridor in Barail Sandstone.",
            "Impact: Lost 65 bbls of KCL-Polymer mud before circulation could be controlled.",
            "Mitigation: Reduced pump rate from 680 gpm to 420 gpm. Pumped 40 bbl high-viscosity LCM pill (nut plug & mica).",
            "Lesson Learned: Pre-treat active system with medium coarse LCM 50m prior to entering Barail Sandstone horizon.",
            "--------------------------------------------------------------------------------",
            "DRILLING PARAMETERS AT TIME OF INCIDENT:",
            "WOB: 22.5 klbs | RPM: 110 | Torque: 14.8 kft-lbs | Mud Weight: 1.28 SG | ECD: 1.34 SG",
            "Flow Rate: 550 gpm | Standpipe Pressure: 2850 psi | ROP: 14.2 m/hr",
            "================================================================================",
            "DATA INTEGRITY: SYNTHETIC DEMO RECORD - NOT REAL CONFIDENTIAL DATA"
        ]
    },
    {
        "filename": "demo_well_W002_DDR.pdf",
        "title": "DAILY DRILLING REPORT - DEMO WELL W002",
        "lines": [
            "================================================================================",
            "DEMO SYNTHETIC DRILLING DATA - OIL INDIA LIMITED HACKATHON PROTOTYPE",
            "================================================================================",
            "Well Name: DEMO-W002 (Offset North-East)",
            "Field: Dikom / Greater Dibrugarh Area",
            "Date: 2024-04-02 | Report Number: DDR-58 | Rig: Synthetic-Rig-02",
            "Depth: 3615.0 m (MD) | Formation: Kopili Formation",
            "--------------------------------------------------------------------------------",
            "OPERATIONAL SUMMARY & INCIDENT DETAILS:",
            "Event: STUCK_PIPE (Differential Sticking Incident)",
            "Severity: HIGH",
            "Observed Symptoms: Overpull observed on connections exceeding 85 klbs; inability to rotate drillstring.",
            "Cause: Reactive swelling shale combined with high differential pressure across depleted Kopili sand stringer.",
            "Impact: 14.5 hours of Non-Productive Time (NPT) spent jarring and circulating pipe-freeing pill.",
            "Mitigation: Spotted 35 bbl hydrocarbon/glycol freeing pill; worked drillstring with hydraulic jar (maximum 110 klbs).",
            "Lesson Learned: Maintain strict mud inhibition and limit stationary connection times to under 3 minutes.",
            "--------------------------------------------------------------------------------",
            "DRILLING PARAMETERS AT TIME OF INCIDENT:",
            "WOB: 26.0 klbs | RPM: 95 | Torque: 19.5 kft-lbs | Mud Weight: 1.32 SG | ECD: 1.39 SG",
            "Flow Rate: 480 gpm | Standpipe Pressure: 3100 psi | ROP: 6.8 m/hr",
            "================================================================================",
            "DATA INTEGRITY: SYNTHETIC DEMO RECORD - NOT REAL CONFIDENTIAL DATA"
        ]
    },
    {
        "filename": "demo_well_W003_WCR.pdf",
        "title": "WELL COMPLETION REPORT - DEMO WELL W003",
        "lines": [
            "================================================================================",
            "DEMO SYNTHETIC DRILLING DATA - OIL INDIA LIMITED HACKATHON PROTOTYPE",
            "================================================================================",
            "Well Name: DEMO-W003 (Offset West)",
            "Field: Dikom / Greater Dibrugarh Area",
            "Date: 2024-05-18 | Final Well Summary Report | Rig: Synthetic-Rig-03",
            "Depth: 3850.0 m (TD) | Target Horizon: Sylhet Limestone",
            "--------------------------------------------------------------------------------",
            "SECTION SUMMARY & CRITICAL WELL CONTROL EVENT:",
            "Event: KICK (Gas Influx / Well Control Event)",
            "Severity: CRITICAL",
            "Observed Symptoms: Rapid pit gain (+32 bbls in 6 minutes), flow check positive with pumps off, shut-in drill pipe pressure (SIDPP) 380 psi.",
            "Cause: Unexpected high pressure gas stringer encountered at 3842 m in Sylhet Limestone top.",
            "Impact: Shut in well using annular preventer; 18 hours well control operation to circulate out kick.",
            "Mitigation: Executed Engineer's Method to kill well. Weighted mud from 1.35 SG to 1.44 SG using barite.",
            "Lesson Learned: Conduct regular slow pump rate (SCR) measurements and keep kill sheet continuously updated.",
            "--------------------------------------------------------------------------------",
            "POST-WELL RECOMMENDATIONS:",
            "Prior to drilling Sylhet Limestone in adjacent blocks, ensure pilot hole or MWD resistivity real-time correlation.",
            "================================================================================",
            "DATA INTEGRITY: SYNTHETIC DEMO RECORD - NOT REAL CONFIDENTIAL DATA"
        ]
    }
]

def create_pdfs():
    print("[INFO] Generating synthetic PDF drilling reports in documents/sample_reports/ ...")
    for r in REPORTS:
        out_path = SAMPLE_DIR / r["filename"]
        c = canvas.Canvas(str(out_path), pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, r["title"])
        
        c.setFont("Courier", 9)
        y = height - 80
        for line in r["lines"]:
            c.drawString(40, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Courier", 9)
                y = height - 50
        c.save()
        print(f"  [CREATED] {out_path.name} ({out_path.stat().st_size} bytes)")
    print("[SUCCESS] All demo PDF reports generated successfully.")

if __name__ == "__main__":
    create_pdfs()
