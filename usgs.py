import os
import json
import pandas as pd
from datetime import datetime, timedelta, timezone
from dataretrieval import waterdata

os.environ["API_USGS_PAT"] = "na4b3hRXYMvROjnnEV2cfpb9Z3OVBdHtqYNZuObN"

df, metadata = waterdata.get_continuous(
    monitoring_location_id=[
        'USGS-06696000', 'USGS-06701630', 'USGS-06701700', 'USGS-06701900', 
        'USGS-06707500', 'USGS-06708000', 'USGS-06709600', 'USGS-06710247', 
        'USGS-06711565', 'USGS-06711575', 'USGS-06711618', 'USGS-06711770', 
        'USGS-06711785', 'USGS-06712000', 'USGS-06714000', 'USGS-06714215', 
        'USGS-06720500', 'USGS-06721000', 'USGS-06724000', 'USGS-06724970', 
        'USGS-06730160', 'USGS-06730200', 'USGS-06741510', 'USGS-06744000', 
        'USGS-06752260', 'USGS-06754000', 'USGS-06758500', 'USGS-06759500', 
        'USGS-06760000', 'USGS-06762500', 'USGS-06763980', 'USGS-06764000', 
        'USGS-06764200'
    ],
    time='PT1H'
)

code_translations = {
    "00010": "Water Temperature (C)",
    "00020": "Air Temperature (C)",
    "00045": "Precipitation (in)",
    "00060": "Streamflow (cfs)",
    "00065": "Gage Height (ft)",
    "00095": "Specific Conductance",
    "00300": "Dissolved Oxygen (mg/L)",
    "00400": "pH",
    "63160": "Water Temperature (F)"
}

json_file_path = "south_platte_24hr.json"
existing_records = []

if os.path.exists(json_file_path):
    try:
        with open(json_file_path, "r") as f:
            existing_records = json.load(f)
    except Exception:
        existing_records = []

new_records = []
for idx, row in df.iterrows():
    raw_code = str(row.get("parameter_code", "")).strip()
    
    matched_label = raw_code
    for code, translation in code_translations.items():
        if code in raw_code:
            matched_label = translation
            break
            
    raw_val = row.get("value")
    clean_val = None if pd.isna(raw_val) else float(raw_val)
    
    clean_row = {
        "gauge_id": str(row.get("monitoring_location_id", "")).strip(),
        "parameter": matched_label,
        "time": str(row.get("time", "")).strip(),
        "value": clean_val,
        "unit": str(row.get("unit_of_measure", "")).strip()
    }
    new_records.append(clean_row)

combined_records = existing_records + new_records

now = datetime.now(timezone.utc)
cutoff_time = now - timedelta(hours=24)

trimmed_records = []
for record in combined_records:
    try:
        record_time = datetime.fromisoformat(record["time"])
        if record_time >= cutoff_time:
            trimmed_records.append(record)
    except Exception:
        trimmed_records.append(record)

for record in trimmed_records:
    param_str = str(record["parameter"]).strip()
    for code, translation in code_translations.items():
        if code in param_str:
            record["parameter"] = translation
            break

with open(json_file_path, "w") as f:
    json.dump(trimmed_records, f, indent=2)
