#!/usr/bin/env python3
"""
NWIS Synthetic Drilling Data Generator
======================================
Generates realistic synthetic datasets for the Nearby Wells Intelligence System prototype.
All records are marked with `is_demo_data=True` and `data_source="SYNTHETIC_GENERATED_DEMO"`.
Geology and well parameters reflect Upper Assam Basin style stratigraphy (Dikom, Moran, Nahorkatiya).

Output Directory: data/demo/
"""

import os
import random
import numpy as np
import pandas as pd
from pathlib import Path

# Fix random seed for reproducible demo datasets
np.random.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# 1. Stratigraphy Definition for Upper Assam Basin (Synthetic Reference)
FORMATIONS = [
    {
        "formation_id": "FMT-001",
        "formation_name": "Alluvium",
        "lithology": "Unconsolidated Sand, Silt, Gravel",
        "age_era": "Recent to Pleistocene",
        "typical_top_depth": 0.0,
        "typical_bottom_depth": 350.0,
        "pore_pressure_gradient_sg": 1.00,
        "fracture_gradient_sg": 1.45,
        "known_hazards": "Surface washouts, high permeability seepage",
        "drillability_rating": "Easy",
        "risk_level": "LOW",
        "color_hex": "#94A3B8"
    },
    {
        "formation_id": "FMT-002",
        "formation_name": "Dhekiajuli Sandstone",
        "lithology": "Coarse Sandstone, Pebble Beds",
        "age_era": "Pliocene",
        "typical_top_depth": 350.0,
        "typical_bottom_depth": 1100.0,
        "pore_pressure_gradient_sg": 1.02,
        "fracture_gradient_sg": 1.52,
        "known_hazards": "Minor seepage loss, bit balling in clayey stringers",
        "drillability_rating": "Easy",
        "risk_level": "LOW",
        "color_hex": "#64748B"
    },
    {
        "formation_id": "FMT-003",
        "formation_name": "Girujan Clay",
        "lithology": "Mottled Plastic Clay, Reactive Shale",
        "age_era": "Miocene",
        "typical_top_depth": 1100.0,
        "typical_bottom_depth": 1950.0,
        "pore_pressure_gradient_sg": 1.05,
        "fracture_gradient_sg": 1.60,
        "known_hazards": "Swelling shale, tight hole during trips, hole enlargement",
        "drillability_rating": "Medium",
        "risk_level": "MEDIUM",
        "color_hex": "#D97706"
    },
    {
        "formation_id": "FMT-004",
        "formation_name": "Tipam Sandstone",
        "lithology": "Medium to Coarse Friable Sandstone",
        "age_era": "Miocene",
        "typical_top_depth": 1950.0,
        "typical_bottom_depth": 2750.0,
        "pore_pressure_gradient_sg": 1.08,
        "fracture_gradient_sg": 1.68,
        "known_hazards": "Partial mud loss, differential sticking, high filtration",
        "drillability_rating": "Easy to Medium",
        "risk_level": "MEDIUM",
        "color_hex": "#3B82F6"
    },
    {
        "formation_id": "FMT-005",
        "formation_name": "Bokabil Formation",
        "lithology": "Interbedded Sandstone, Siltstone, Silt-Shale",
        "age_era": "Miocene",
        "typical_top_depth": 2750.0,
        "typical_bottom_depth": 3150.0,
        "pore_pressure_gradient_sg": 1.15,
        "fracture_gradient_sg": 1.72,
        "known_hazards": "Transition pressure ramp-up, pack-off risks, minor gas kicks",
        "drillability_rating": "Medium",
        "risk_level": "HIGH",
        "color_hex": "#8B5CF6"
    },
    {
        "formation_id": "FMT-006",
        "formation_name": "Barail Sandstone",
        "lithology": "Fine to Medium Quartzose Sandstone, Coal Streaks",
        "age_era": "Oligocene",
        "typical_top_depth": 3150.0,
        "typical_bottom_depth": 3700.0,
        "pore_pressure_gradient_sg": 1.28,
        "fracture_gradient_sg": 1.82,
        "known_hazards": "High pressure gas zones, severe differential sticking, mud loss in depleted streaks",
        "drillability_rating": "Medium",
        "risk_level": "HIGH",
        "color_hex": "#10B981"
    },
    {
        "formation_id": "FMT-007",
        "formation_name": "Barail Coal-Shale",
        "lithology": "Carbonaceous Splintery Shale, Sub-bituminous Coal",
        "age_era": "Oligocene",
        "typical_top_depth": 3700.0,
        "typical_bottom_depth": 3950.0,
        "pore_pressure_gradient_sg": 1.34,
        "fracture_gradient_sg": 1.88,
        "known_hazards": "Severe hole collapse, torque spikes, pack-off, stuck pipe",
        "drillability_rating": "Hard",
        "risk_level": "CRITICAL",
        "color_hex": "#EF4444"
    },
    {
        "formation_id": "FMT-008",
        "formation_name": "Kopili Formation",
        "lithology": "Splintery Black Shale, Calcareous Siltstone",
        "age_era": "Eocene",
        "typical_top_depth": 3950.0,
        "typical_bottom_depth": 4350.0,
        "pore_pressure_gradient_sg": 1.42,
        "fracture_gradient_sg": 1.95,
        "known_hazards": "Abnormal overpressure gas kick, sloughing shale",
        "drillability_rating": "Hard",
        "risk_level": "HIGH",
        "color_hex": "#EC4899"
    },
    {
        "formation_id": "FMT-009",
        "formation_name": "Sylhet Limestone",
        "lithology": "Hard Fossiliferous Vuggy Limestone",
        "age_era": "Eocene",
        "typical_top_depth": 4350.0,
        "typical_bottom_depth": 4700.0,
        "pore_pressure_gradient_sg": 1.10,
        "fracture_gradient_sg": 1.70,
        "known_hazards": "Total lost circulation (cavernous/vuggy), H2S traces, slow ROP",
        "drillability_rating": "Very Hard",
        "risk_level": "CRITICAL",
        "color_hex": "#F97316"
    },
    {
        "formation_id": "FMT-010",
        "formation_name": "Disang Formation",
        "lithology": "Tectonic Splintery Dark Slate & Hard Quartzite",
        "age_era": "Paleocene to Cretaceous",
        "typical_top_depth": 4700.0,
        "typical_bottom_depth": 5200.0,
        "pore_pressure_gradient_sg": 1.38,
        "fracture_gradient_sg": 1.98,
        "known_hazards": "Severe vibration, twist-off risk, high temperature",
        "drillability_rating": "Abrasive / Extreme",
        "risk_level": "HIGH",
        "color_hex": "#6366F1"
    }
]

# 2. Generate Synthetic Wells
FIELDS = ["Dikom", "Nahorkatiya", "Moran", "Baghjan", "Jorajan", "Tengakhat", "Kumchai", "Shalmari"]
BASE_LAT = 27.4200
BASE_LON = 95.3200

wells_data = []

# Active Well (WELL-001)
wells_data.append({
    "well_id": "WELL-001",
    "well_name": "Dikom-104A",
    "field": "Dikom",
    "block": "Dibrugarh ML",
    "basin": "Assam-Arakan",
    "operator": "OIL India Limited (Synthetic Prototype)",
    "well_type": "Development",
    "status": "Drilling",
    "target_depth": 4300.0,
    "current_depth": 3420.0, # Currently in Barail Sandstone near critical loss/stuck zone
    "latitude": round(BASE_LAT, 5),
    "longitude": round(BASE_LON, 5),
    "spud_date": "2026-01-10",
    "completion_date": "",
    "is_active_well": True,
    "is_demo_data": True,
    "data_source": "SYNTHETIC_GENERATED_DEMO"
})

# Offset / Historical Wells (WELL-002 to WELL-030)
for i in range(2, 31):
    well_id = f"WELL-{i:03d}"
    fld = random.choice(FIELDS)
    w_num = random.randint(12, 185)
    w_name = f"{fld}-{w_num}"
    
    # Distance clustering: 5 wells very close (< 3 km), 10 wells close (3-10 km), rest 10-35 km
    if i <= 6:
        radius_deg = random.uniform(0.008, 0.025) # ~1 to 3 km
    elif i <= 16:
        radius_deg = random.uniform(0.025, 0.09)  # ~3 to 10 km
    else:
        radius_deg = random.uniform(0.09, 0.32)   # ~10 to 35 km
        
    angle = random.uniform(0, 2 * np.pi)
    lat = BASE_LAT + radius_deg * np.cos(angle)
    lon = BASE_LON + radius_deg * np.sin(angle)
    
    td = round(random.choice([3850.0, 4100.0, 4250.0, 4450.0, 4650.0, 4900.0]), 1)
    status = random.choice(["Completed", "Completed", "Suspended", "Plugged & Abandoned"])
    w_type = random.choice(["Development", "Development", "Exploratory", "Delineation"])
    
    wells_data.append({
        "well_id": well_id,
        "well_name": w_name,
        "field": fld,
        "block": f"{fld} Block",
        "basin": "Assam-Arakan",
        "operator": "OIL India Limited (Synthetic Prototype)",
        "well_type": w_type,
        "status": status,
        "target_depth": td,
        "current_depth": td,
        "latitude": round(lat, 5),
        "longitude": round(lon, 5),
        "spud_date": f"202{random.randint(1,5)}-0{random.randint(1,9)}-15",
        "completion_date": f"202{random.randint(2,5)}-1{random.randint(0,2)}-20",
        "is_active_well": False,
        "is_demo_data": True,
        "data_source": "SYNTHETIC_GENERATED_DEMO"
    })

# 3. Generate Historical Drilling Events
EVENT_TYPES = [
    "MUD_LOSS", "KICK", "STUCK_PIPE", "TORQUE_SPIKE", "PACK_OFF", 
    "OVERPRESSURE", "WELL_CONTROL", "FISHING", "CEMENTING_ISSUE", "LOST_CIRCULATION"
]

events_data = []
event_counter = 1

EVENT_TEMPLATES = {
    "MUD_LOSS": {
        "cause": "Encountered depleted sandstone reservoir streak with low pore pressure relative to active mud column.",
        "impact": "Sudden drop in active pit volume by 45 bbls; standpipe pressure dropped by 180 psi.",
        "mitigation": "Reduced mud pump rate to 1800 LPM, pumped 35 bbl high-fluid-loss LCM pill (medium calcium carbonate + walnut shells), reduced mud weight from 1.32 to 1.26 SG.",
        "lesson_learned": "Pre-treat active system with fine CaCO3 before penetrating upper Barail Sand boundary. Monitor flow paddle response diligently.",
        "severity": "HIGH",
        "npt": 18.5
    },
    "STUCK_PIPE": {
        "cause": "Differential sticking while stationary for survey across permeable Barail Sand with 450 psi overbalance.",
        "impact": "Drillstring unable to reciprocate or rotate; overpull reached 65 tons with zero pipe movement.",
        "mitigation": "Spotted 40 bbl lubricating oil-based pipe-freeing pill across stuck interval; applied maximum torque (24 kNm) and jarred downward with hydraulic jar for 4.5 hours.",
        "lesson_learned": "Never keep drillstring stationary for > 3 minutes across Barail formation. Maintain pipe rotation and use low-gravity solids control.",
        "severity": "CRITICAL",
        "npt": 34.0
    },
    "KICK": {
        "cause": "Drilled into unexpected high-pressure gas pocket in lower Bokabil / upper Barail transition zone.",
        "impact": "Pit gain of 18 bbls observed with active gas influx; shut-in drillpipe pressure (SIDPP) stabilized at 320 psi, SICP at 410 psi.",
        "mitigation": "Shut in well using annular preventer, verified shut-in pressures, circulated gas influx out via choke manifold using Wait and Weight method with 1.36 SG kill mud.",
        "lesson_learned": "Perform flow check on any ROP drilling break > 4 m/hr. Ensure degasser and trip tank level sensors are calibrated.",
        "severity": "CRITICAL",
        "npt": 26.5
    },
    "TORQUE_SPIKE": {
        "cause": "High dogleg severity and sloughing shale cavings creating keyseating and friction in 8.5 inch section.",
        "impact": "Erratic rotary torque surging from 14 kNm to 28 kNm; top drive stalled twice.",
        "mitigation": "Picked up off bottom, increased flow rate to maximum hole cleaning threshold (2400 LPM), pumped 20 bbl high-viscosity sweep, performed short wiper trip.",
        "lesson_learned": "Maintain hole inclination change below 2.5 deg/30m in Girujan and Barail Shale sections.",
        "severity": "MEDIUM",
        "npt": 8.0
    },
    "PACK_OFF": {
        "cause": "Severe shale sloughing and inadequate cutting transport leading to annular bridge around BHA stabilizers.",
        "impact": "Sudden pressure spike of 900 psi on standpipe; total loss of returns due to annular bridging.",
        "mitigation": "Immediately stopped pumps, worked drillstring with light tension, slowly re-established circulation at low rate (800 LPM) while rotating at 40 RPM.",
        "lesson_learned": "Increase polymer encapsulation concentration and optimize flow rheology (YP > 22 lb/100ft2) before drilling Barail Coal-Shale.",
        "severity": "HIGH",
        "npt": 14.0
    },
    "LOST_CIRCULATION": {
        "cause": "Penetrated open micro-fractures in Sylhet Limestone formation.",
        "impact": "100% loss of drilling fluid returns; pit level dropped rapidly.",
        "mitigation": "Pumped heavy bridging LCM blend followed by gunk plug (diesel-bentonite-cement); cured loss zone and resumed blind drilling with water cap.",
        "lesson_learned": "Prepare pre-mixed LCM tanks and fibrous loss materials prior to penetrating top of Sylhet Limestone.",
        "severity": "CRITICAL",
        "npt": 48.0
    },
    "CEMENTING_ISSUE": {
        "cause": "Channeling of cement slurry due to poor mud cake removal and incomplete hole cleaning across washed out section.",
        "impact": "CBL-VDL log indicated poor bond quality across target production reservoir interval.",
        "mitigation": "Perforated squeeze holes at 3380 m and executed block squeeze cementing with microfine cement at 2800 psi.",
        "lesson_learned": "Run centralizers at 1 per joint across hydrocarbon zones and utilize high-energy weighted spacer with chemical wash.",
        "severity": "HIGH",
        "npt": 38.0
    }
}

# Generate 150+ realistic events distributed across offset wells
for well in wells_data:
    w_id = well["well_id"]
    # Assign 3 to 8 events per well
    num_events = random.randint(4, 8) if w_id != "WELL-001" else 3
    for _ in range(num_events):
        event_type = random.choice(list(EVENT_TEMPLATES.keys()))
        tmpl = EVENT_TEMPLATES[event_type]
        
        # Pick realistic formation & depth
        fmt_obj = random.choice(FORMATIONS[2:]) # From Girujan Clay downwards
        depth_start = round(random.uniform(fmt_obj["typical_top_depth"] + 20, fmt_obj["typical_bottom_depth"] - 30), 1)
        depth_end = round(depth_start + random.uniform(5, 45), 1)
        
        # Specific historical cluster around 3400-3450 m in Barail Sandstone for high-fidelity demo scenario
        if w_id in ["WELL-002", "WELL-003", "WELL-005", "WELL-008", "WELL-012"] and event_type in ["MUD_LOSS", "STUCK_PIPE", "KICK"]:
            depth_start = round(random.uniform(3410.0, 3445.0), 1)
            depth_end = round(depth_start + random.uniform(8, 25), 1)
            fmt_obj = FORMATIONS[5] # Barail Sandstone
            
        events_data.append({
            "event_id": f"EVT-{event_counter:04d}",
            "well_id": w_id,
            "event_type": event_type,
            "start_depth": depth_start,
            "end_depth": depth_end,
            "formation": fmt_obj["formation_name"],
            "severity": tmpl["severity"],
            "cause": tmpl["cause"],
            "impact": tmpl["impact"],
            "mitigation": tmpl["mitigation"],
            "lesson_learned": tmpl["lesson_learned"],
            "npt_hours": round(tmpl["npt"] * random.uniform(0.8, 1.4), 1),
            "source_document": f"{well['well_name']}_DDR_Final_Report.pdf",
            "source_page": random.randint(1, 45),
            "confidence": round(random.uniform(0.88, 0.98), 2),
            "is_demo_data": True
        })
        event_counter += 1

# 4. Generate High-Resolution Telemetry & Drilling Parameters (5000+ points)
parameters_data = []
param_counter = 1

# Map events by well for fast lookup during parameter generation
well_events_map = {}
for ev in events_data:
    w = ev["well_id"]
    if w not in well_events_map:
        well_events_map[w] = []
    well_events_map[w].append(ev)

for well in wells_data:
    w_id = well["well_id"]
    td = well["target_depth"]
    step = 5.0 if w_id == "WELL-001" else 15.0
    depth_range = np.arange(100.0, (well["current_depth"] if w_id == "WELL-001" else td) + step, step)
    ev_list = well_events_map.get(w_id, [])

    for d in depth_range:
        current_fmt = "Alluvium"
        for fmt in FORMATIONS:
            if fmt["typical_top_depth"] <= d <= fmt["typical_bottom_depth"]:
                current_fmt = fmt["formation_name"]
                break

        # Geological baselines
        base_rop = 18.0 if d < 1200 else (12.0 if d < 2800 else 8.5)
        base_wob = 8.0 if d < 1200 else (14.0 if d < 2800 else 18.5)
        base_rpm = 120 if d < 2000 else 100
        base_torque = 6.5 + (d / 500.0) * 1.8
        base_spp = 1400 + (d / 10.0) * 3.5
        base_flow = 2200 if d < 1500 else 1850
        base_mw = 1.05 if d < 1200 else (1.18 if d < 2800 else 1.28)
        base_ecd = base_mw + 0.05
        base_hkld = 85.0 + (d / 100.0) * 4.2

        # Check if depth overlaps any active event on this well
        active_ev_type = None
        for ev in ev_list:
            if ev["start_depth"] <= d <= ev["end_depth"]:
                active_ev_type = ev["event_type"]
                break

        # For active well WELL-001 at 3405-3435m, introduce loss & torque anomaly
        if w_id == "WELL-001" and 3405 <= d <= 3435:
            active_ev_type = "MUD_LOSS"

        # Apply realistic physical drilling signatures based on incident type
        if active_ev_type in ["MUD_LOSS", "LOST_CIRCULATION"]:
            base_spp -= random.uniform(120, 220)
            base_flow -= random.uniform(90, 180)
            base_torque += random.uniform(1.5, 4.0)
            base_rop *= 0.65
            base_ecd -= 0.02
        elif active_ev_type in ["STUCK_PIPE", "TORQUE_SPIKE", "PACK_OFF"]:
            base_torque += random.uniform(4.5, 9.0)
            base_rop *= 0.35
            base_spp += random.uniform(150, 350)
            base_hkld += random.uniform(15.0, 35.0)
        elif active_ev_type in ["KICK", "OVERPRESSURE", "WELL_CONTROL"]:
            base_rop *= 1.8
            base_flow += random.uniform(80, 160)
            base_spp -= random.uniform(50, 120)
            base_ecd -= 0.04

        parameters_data.append({
            "id": param_counter,
            "well_id": w_id,
            "depth": round(float(d), 1),
            "rop": round(float(max(1.0, base_rop + np.random.normal(0, 0.8))), 2),
            "wob": round(float(max(2.0, base_wob + np.random.normal(0, 0.6))), 2),
            "rpm": round(float(max(30.0, base_rpm + np.random.normal(0, 2.0))), 1),
            "torque": round(float(max(1.0, base_torque + np.random.normal(0, 0.5))), 2),
            "standpipe_pressure": round(float(base_spp + np.random.normal(0, 15.0)), 1),
            "flow_rate": round(float(base_flow + np.random.normal(0, 15.0)), 1),
            "mud_weight": round(float(base_mw), 2),
            "ecd": round(float(base_ecd), 2),
            "hook_load": round(float(base_hkld + np.random.normal(0, 1.2)), 1),
            "inclination": round(float(0.5 + (d / 1000.0) * 1.2), 2),
            "azimuth": round(float(45.0 + np.sin(d/300.0) * 15.0), 1),
            "formation_name": current_fmt,
            "hole_size": 17.5 if d < 350 else (12.25 if d < 1950 else 8.5),
            "bit_type": "PDC 5-blade",
            "is_simulated": (w_id == "WELL-001"),
            "is_demo_data": True
        })
        param_counter += 1

# 5. Casing and Cementing Programs
casing_data = []
cementing_data = []
mud_prog_data = []
c_id = 1
cm_id = 1
mp_id = 1

for well in wells_data:
    w_id = well["well_id"]
    td = well["target_depth"]
    
    # Casing strings
    c_specs = [
        {"type": "Conductor", "hole": 26.0, "casing": 20.0, "top": 0.0, "shoe": 80.0, "wt": 94.0, "gr": "K-55"},
        {"type": "Surface", "hole": 17.5, "casing": 13.375, "top": 0.0, "shoe": 1100.0, "wt": 68.0, "gr": "N-80"},
        {"type": "Intermediate", "hole": 12.25, "casing": 9.625, "top": 0.0, "shoe": 2950.0, "wt": 47.0, "gr": "P-110"},
        {"type": "Production Liner", "hole": 8.5, "casing": 7.0, "top": 2800.0, "shoe": td, "wt": 29.0, "gr": "Q-125"}
    ]
    for cs in c_specs:
        casing_data.append({
            "id": c_id,
            "well_id": w_id,
            "casing_type": cs["type"],
            "hole_size": cs["hole"],
            "casing_size": cs["casing"],
            "top_depth": cs["top"],
            "shoe_depth": cs["shoe"],
            "weight_ppf": cs["wt"],
            "grade": cs["gr"],
            "is_demo_data": True
        })
        # Cementing for each casing
        cementing_data.append({
            "id": cm_id,
            "well_id": w_id,
            "casing_type": cs["type"],
            "slurry_type": "Class G + 0.2% Antifoam + Silica Flour" if cs["type"] != "Conductor" else "QuickSet Pozzolan",
            "slurry_density_ppg": 15.8 if cs["type"] != "Conductor" else 14.2,
            "top_of_cement_depth": max(0.0, cs["top"]),
            "volume_bbls": round(float(random.randint(180, 420)), 1),
            "pressure_psi": round(float(random.randint(1800, 3200)), 1),
            "remarks": "Bumped plug with 500 psi overbalance. Floats held.",
            "is_demo_data": True
        })
        c_id += 1
        cm_id += 1
        
    # Mud Program
    m_specs = [
        {"from": 0.0, "to": 1100.0, "type": "Bentonite Spud Mud", "min_mw": 1.04, "max_mw": 1.08, "visc": 38, "pv": 12, "yp": 18, "ph": 9.0},
        {"from": 1100.0, "to": 2950.0, "type": "KCL-Polymer Inhibitive Mud", "min_mw": 1.15, "max_mw": 1.22, "visc": 48, "pv": 18, "yp": 24, "ph": 9.5},
        {"from": 2950.0, "to": td, "type": "Low-Solids Non-Dispersed Polymer", "min_mw": 1.25, "max_mw": 1.34, "visc": 54, "pv": 22, "yp": 28, "ph": 9.8}
    ]
    for ms in m_specs:
        mud_prog_data.append({
            "id": mp_id,
            "well_id": w_id,
            "from_depth": ms["from"],
            "to_depth": ms["to"],
            "mud_type": ms["type"],
            "mud_weight_min": ms["min_mw"],
            "mud_weight_max": ms["max_mw"],
            "viscosity": ms["visc"],
            "pv": ms["pv"],
            "yp": ms["yp"],
            "ph": ms["ph"],
            "is_demo_data": True
        })
        mp_id += 1

# 6. Well Trajectories
trajectories_data = []
traj_id = 1
for well in wells_data:
    w_id = well["well_id"]
    td = well["target_depth"]
    step = 50.0
    for md in np.arange(0.0, td + step, step):
        inc = 0.0 if md < 1000 else min(35.0, (md - 1000) * 0.015)
        az = 45.0
        tvd = md * np.cos(np.radians(inc))
        east = md * np.sin(np.radians(inc)) * np.sin(np.radians(az))
        north = md * np.sin(np.radians(inc)) * np.cos(np.radians(az))
        trajectories_data.append({
            "id": traj_id,
            "well_id": w_id,
            "measured_depth": round(float(md), 1),
            "true_vertical_depth": round(float(tvd), 1),
            "inclination": round(float(inc), 2),
            "azimuth": round(float(az), 1),
            "dogleg_severity": round(float(0.4 if md > 1000 else 0.0), 2),
            "easting": round(float(east), 2),
            "northing": round(float(north), 2)
        })
        traj_id += 1

# Save all datasets to CSV
pd.DataFrame(wells_data).to_csv(DEMO_DIR / "wells.csv", index=False)
pd.DataFrame(FORMATIONS).to_csv(DEMO_DIR / "formations.csv", index=False)
pd.DataFrame(events_data).to_csv(DEMO_DIR / "drilling_events.csv", index=False)
pd.DataFrame(parameters_data).to_csv(DEMO_DIR / "drilling_parameters.csv", index=False)
pd.DataFrame(casing_data).to_csv(DEMO_DIR / "casing.csv", index=False)
pd.DataFrame(cementing_data).to_csv(DEMO_DIR / "cementing.csv", index=False)
pd.DataFrame(mud_prog_data).to_csv(DEMO_DIR / "mud_programs.csv", index=False)
pd.DataFrame(trajectories_data).to_csv(DEMO_DIR / "trajectories.csv", index=False)

print(f" Synthetic demo datasets successfully generated in: {DEMO_DIR}")
print(f"   - Wells: {len(wells_data)}")
print(f"   - Formations: {len(FORMATIONS)}")
print(f"   - Historical Events: {len(events_data)}")
print(f"   - Drilling Telemetry Records: {len(parameters_data)}")
print(f"   - Casing Records: {len(casing_data)}")
print(f"   - Cementing Records: {len(cementing_data)}")
print(f"   - Mud Program Records: {len(mud_prog_data)}")
print(f"   - Trajectory Records: {len(trajectories_data)}")
