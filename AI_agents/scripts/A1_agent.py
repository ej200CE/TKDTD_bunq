#!/usr/bin/env python3
"""
A1_agent.py  –  now emits Vega‑Lite specs
──────────────────────────────────────────
• Reads simulated_data.json
• Consults optional prefs/<user>.txt
• Asks NVIDIA NIM to RETURN VALID VEGA‑LITE JSON specs
• Saves dashboards/<user>_<YYYY‑MM>.json
"""

from __future__ import annotations
import json, sys, pathlib, datetime as dt
from collections import Counter
import pandas as pd
from openai import OpenAI

# ------- folders ----------------------------------------------------------
HERE   = pathlib.Path(__file__).resolve()
ROOT   = HERE.parent.parent
RAW    = ROOT / "data" / "simulated_data.json"
PREFS  = ROOT / "prefs"
DASH   = ROOT / "dashboards"; DASH.mkdir(exist_ok=True)

# ------- NVIDIA NIM creds -------------------------------------------------
NIM_KEY   = "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"
NIM_MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1"
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NIM_KEY)

SYSTEM = (
    "You are a BI assistant that returns Vega‑Lite JSON.\n"
    "RULES:\n"
    " • Output ONLY a JSON array named dashboard_plan.\n"
    " • Each array item MUST be a valid Vega‑Lite spec.\n"
    " • Do NOT wrap in markdown, do NOT add explanations.\n"
)

# ------- helpers ----------------------------------------------------------
def pref(user: str) -> str | None:
    f = PREFS / f"{user}.txt"
    return f.read_text().strip() if f.exists() else None

def metrics(df: pd.DataFrame) -> dict:
    df["year_month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    return {
        "total": round(df["value"].sum(), 2),
        "top_descr": Counter(df["description"]).most_common(5),
    }

def ask_llm(metrics: dict, pref_text: str | None) -> list[dict]:
    prompt = (
        f"Metrics: {json.dumps(metrics)}\n"
        f"User preference: {pref_text or 'None'}\n\n"
        "Return JSON with key dashboard_plan = list of Vega‑Lite specs.\n"
        "Example element:\n"
        "{"
        '  "mark": "bar",'
        '  "encoding": { "x": {"field":"description","type":"nominal"},'
        '                "y": {"aggregate":"sum","field":"value"} }'
        "}"
    )
    resp = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
    )
    text = resp.choices[0].message.content
    try:
        return json.loads(text)["dashboard_plan"]
    except Exception:
        return []

# ------- main -------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python A1_agent.py <user>")
    user = sys.argv[1]

    if not RAW.exists():
        sys.exit("simulated_data.json missing; run generator.")
    df = pd.read_json(RAW)

    pref_text = pref(user)
    dash_plan = ask_llm(metrics(df), pref_text)

    out = DASH / f"{user}_{dt.datetime.utcnow():%Y-%m}.json"
    json.dump(
        {
            "generated_at": dt.datetime.utcnow().isoformat(),
            "metrics": metrics(df),
            "preference": pref_text,
            "dashboard_plan": dash_plan,
        },
        open(out, "w"),
        indent=2,
    )
    print("🪄  wrote", out.relative_to(ROOT))

if __name__ == "__main__":
    main()
