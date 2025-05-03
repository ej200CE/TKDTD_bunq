#!/usr/bin/env python3
"""
A2_agent.py  –  chat/batch agent, saves extended Markdown reports

Usage
  python A2_agent.py chat  <user>
  python A2_agent.py batch <user>
"""

from __future__ import annotations
import json, re, sys, pathlib, socket, subprocess, datetime as dt
from openai import OpenAI

# ─── paths ───────────────────────────────────────────────────────────────
HERE  = pathlib.Path(__file__).resolve()
ROOT  = HERE.parent.parent            # AI_agents/
DASH  = ROOT / "dashboards"
PREF  = ROOT / "prefs"
REPO  = ROOT / "reports"; REPO.mkdir(exist_ok=True)

# ─── NVIDIA creds ────────────────────────────────────────────────────────
NIM_KEY   = "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"
NIM_MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1"

client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NIM_KEY)

SYS_MSG = (
    "You are a personal‑finance assistant.\n"
    "RULES:\n"
    " • Never reveal chain‑of‑thought.\n"
    " • Produce clear, helpful answers.\n"
)
STRIP_COT = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)

# ─── Streamlit auto‑launcher ─────────────────────────────────────────────
def ensure_viewer_running(user: str):
    def port_open(p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", p)) == 0
    if port_open(8501):
        return
    view = HERE.parent / "st_viewer.py"
    print("🔄 starting Streamlit viewer on http://localhost:8501 …")
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run",
         str(view), "--", "--user", user],
        cwd=str(ROOT)
    )

# ─── helpers ─────────────────────────────────────────────────────────────
def latest_dash(user: str) -> pathlib.Path | None:
    files = sorted(DASH.glob(f"{user}_*.json"))
    return files[-1] if files else None

def user_pref(user: str) -> str | None:
    p = PREF / f"{user}.txt"
    return p.read_text().strip() if p.exists() else None

def save_pref(user: str, txt: str):
    PREF.mkdir(exist_ok=True)
    (PREF / f"{user}.txt").write_text(txt.strip())

def call_llm(prompt: str, concise: bool = True) -> str:
    """Return a concise or extended answer depending on flag."""
    if concise:
        full_prompt = prompt + "\n\nRespond in 2‑3 sentences."
    else:
        full_prompt = prompt + (
            "\n\nWrite a detailed explanation, at least 200 words, "
            "in Markdown format."
        )
    resp = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[{"role": "system", "content": SYS_MSG},
                  {"role": "user", "content": full_prompt}],
        max_tokens=600 if not concise else 300,
        temperature=0.5,
    )
    return STRIP_COT.sub("", resp.choices[0].message.content.strip())

def save_report(user: str, content_md: str):
    ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")
    path = REPO / f"{user}_{ts}.md"
    path.write_text(content_md)
    print(f"📝 extended report saved → {path.relative_to(ROOT)}")

# ─── batch mode ──────────────────────────────────────────────────────────
def batch(user: str):
    dp = latest_dash(user)
    if not dp:
        sys.exit("❌ No dashboard found. Run A1 first.")
    dash = json.load(open(dp))
    prompt_base = (
        f"Dashboard metrics JSON:\n{json.dumps(dash['metrics'])}\n\n"
        f"User preference: {dash.get('preference') or 'None'}\n"
        "Provide recommendations."
    )
    short = call_llm(prompt_base, concise=True)
    long  = call_llm(prompt_base, concise=False)
    save_report(user, long)
    print(short)

# ─── chat mode ───────────────────────────────────────────────────────────
def chat(user: str):
    print("🔹 Chat mode (/help for commands)")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye"); break
        if not line:
            continue

        if line == "/quit":
            break
        if line == "/help":
            print("/goal <text>   set preference\n"
                  "/dashboard      refresh dashboard (runs A1)\n"
                  "/quit           exit chat")
            continue
        if line.startswith("/goal"):
            txt = line[len("/goal"):].strip()
            if txt:
                save_pref(user, txt)
                print("👍 preference saved.")
            else:
                print("Usage: /goal Spend less on coffee")
            continue
        if line == "/dashboard":
            ensure_viewer_running(user)
            subprocess.run(["python", str(HERE.parent / "A1_agent.py"), user])
            print("✅ dashboard refreshed.")
            continue

        dp = latest_dash(user)
        prompt_base = (
            f"Dashboard JSON: {dp.read_text() if dp else '{}'}\n"
            f"User preference: {user_pref(user) or 'None'}\n"
            f"Question: {line}\n"
        )
        short = call_llm(prompt_base, concise=True)
        long  = call_llm(prompt_base, concise=False)
        save_report(user, f"## Q: {line}\n\n{long}")
        print(short)

# ─── CLI dispatcher ──────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 3:
        sys.exit("Usage:\n  python A2_agent.py chat  <user>\n"
                 "  python A2_agent.py batch <user>")
    mode, user = sys.argv[1:3]
    if mode == "chat":
        chat(user)
    elif mode == "batch":
        batch(user)
    else:
        sys.exit("Mode must be 'chat' or 'batch'.")

if __name__ == "__main__":
    main()
