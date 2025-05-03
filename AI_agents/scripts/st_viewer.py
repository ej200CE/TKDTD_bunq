#!/usr/bin/env python3
"""
st_viewer.py  –  Streamlit dashboard renderer
Run:
    streamlit run AI_agents/scripts/st_viewer.py -- --user demo
"""

import json, argparse, pathlib, pandas as pd, streamlit as st

# parse CLI arg passed through Streamlit
parser = argparse.ArgumentParser()
parser.add_argument("--user", required=True)
args = parser.parse_args()

ROOT   = pathlib.Path(__file__).resolve().parent.parent
DATA   = ROOT / "data" / "simulated_data.json"
DASHES = ROOT / "dashboards"

# get latest dashboard
dash_file = max(DASHES.glob(f"{args.user}_*.json"))
dash      = json.load(open(dash_file))

st.title(f"Dashboard – {args.user} – {dash_file.stem.split('_')[1]}")
st.markdown(f"**Generated**: {dash['generated_at']}")
if dash.get("preference"):
    st.markdown(f"**User goal:** {dash['preference']}")

df = pd.read_json(DATA)

for i, spec in enumerate(dash["dashboard_plan"], 1):
    st.subheader(f"Chart {i}")
    st.vega_lite_chart(df, spec, use_container_width=True)
