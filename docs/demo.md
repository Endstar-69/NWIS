# NWIS 5-Minute Hackathon Demo Script

This document provides a step-by-step presentation script designed for pitching the **Nearby Wells Intelligence System (NWIS)** to OIL India leadership, judges, and domain engineers in under 5 minutes.

---

## ⏱️ Demo Outline & Flow

```text
[0:00 - 0:45] 1. Login & Executive Dashboard (The Problem)
[0:45 - 1:30] 2. Geospatial Intelligence & Offset Well Correlation (Spatial Memory)
[1:30 - 2:15] 3. Multi-Well Stratigraphy & Event Comparison (Offset Analysis)
[2:15 - 3:00] 4. Document Intelligence & Knowledge Ingestion (Unstructured to Structured)
[3:00 - 3:45] 5. Grounded RAG Assistant & Semantic Search (Instant Recall)
[3:45 - 4:30] 6. Live Drilling Telemetry Simulation, ML Risk & Proactive Alerts (Live eRTMAC)
[4:30 - 5:00] 7. Evidence-Backed Recommendation & Summary (Closing)
```

---

## Step-by-Step Presentation Script

### Step 1: Login & Executive Dashboard (0:00 – 0:45)
- **Action**: Open `http://localhost:5173`. Log in with username `engineer` and password `engineer123`.
- **Narration**:
  > *"Good morning judges. Every time OIL India drills a development or exploration well, years of valuable historical drilling experience remain trapped inside static DDRs and WCR completion reports. NWIS bridges this gap by acting as an institutional memory system working seamlessly alongside the eRTMAC concept."*
- **Highlight**: Point out the **DEMO / SYNTHETIC DATA** banner, active well KPI cards (Depth, Formation, ROP, Standpipe Pressure), and the real-time Risk Summary radar.

---

### Step 2: Geospatial Intelligence & Offset Well Search (0:45 – 1:30)
- **Action**: Navigate to **Nearby Wells Map** in the sidebar.
- **Narration**:
  > *"Here we see our active well DEMO-W001 in the Dikom field surrounded by 29 historical offset wells. We can dynamically adjust the search radius from 1 km to 50 km."*
- **Interactive Action**: Click on offset well `DEMO-W002` (4.1 km away). Notice the multi-factor **Similarity Score (88%)** calculated from spatial distance, formation overlap, depth, and historical incident patterns.

---

### Step 3: Multi-Well Comparison (1:30 – 2:15)
- **Action**: Open the **Well Comparison** page. Compare Active Well `DEMO-W001` with `DEMO-W002` and `DEMO-W003`.
- **Narration**:
  > *"Rather than manually flipping through three 50-page reports, the engineer gets an instant side-by-side lithology, casing program, and historical incident depth correlation."*

---

### Step 4: Document Intelligence Pipeline (2:15 – 3:00)
- **Action**: Navigate to **Document Intelligence**. Click upload and select `documents/sample_reports/demo_well_W001_DDR.pdf`.
- **Narration**:
  > *"When a field engineer uploads a daily drilling report or completion report (PDF or TXT), our automated extraction pipeline extracts structured entities: depth, formation, incident taxonomy, root cause, symptoms, and mitigations with a confidence score of 96%."*
- **Highlight**: Show the structured JSON/card extracted directly from the PDF report.

---

### Step 5: Grounded Knowledge Search & AI Assistant (3:00 – 3:45)
- **Action**: Navigate to **Knowledge Search**.
- **Interactive Query**: Click sample prompt: *"What happened in nearby wells around 3420m in Barail Sandstone?"*
- **Narration**:
  > *"Our RAG assistant performs vector semantic search across the historical event repository and synthesizes a grounded answer with exact well IDs, depths, and cited lessons learned—with zero hallucination."*

---

### Step 6: Real-Time Telemetry & Proactive ML Alerts (3:45 – 4:30)
- **Action**: Navigate to **Active Well Intelligence**. Click **"Start Live Telemetry Stream"**.
- **Narration**:
  > *"As our simulated eRTMAC live stream progresses from 3400m to 3422m, our Random Forest risk models detect a loss signature (drop in SPP and negative flow delta). Combined with historical loss incidents in 4 nearby offset wells, the Mud Loss risk surges to 86% (CRITICAL)."*
- **Highlight**: Point out the live telemetry graphs, instant risk pill change, and the new **CRITICAL ALERT** generated in the top banner.

---

### Step 7: Evidence-Linked Recommendations & Closing (4:30 – 5:00)
- **Action**: Scroll down to the **Recommendations & Historical Evidence** section on the Active Well page.
- **Narration**:
  > *"NWIS does not issue blind automated commands. It provides explainable decision support: citing exact offset loss incidents in W002 and W003, and recommending proactive LCM treatment and pump rate adjustments before reaching total lost circulation.*
  >
  > *NWIS transforms static historical documents into proactive, wellsite-ready intelligence for safer, more efficient drilling operations at OIL India. Thank you!"*

---

## 🚀 Quick Automated Demo Script

You can also run the full end-to-end pipeline in one terminal command:
```powershell
python scripts/run_demo.py
```
