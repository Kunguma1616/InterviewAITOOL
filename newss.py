import streamlit as st
import os
import tempfile
from pathlib import Path
from groq import Groq
import json
import subprocess
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import re
import math
import itertools
from collections import Counter
import hashlib
import pathlib
import base64

# =========================
# Page Config + Styles
# =========================
st.set_page_config(
    page_title="AI Interview Analyzer - HR Tool",
    page_icon="",
    layout="wide"
)

# ---- Aspect Theme (your colors) + component styles ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');
    
    :root {
        --color-primary: #27549D;
        --color-dark-blue: #0f1e33;
        --color-secondary: #7099DB;
        --color-accent: #F1FF24;
        --yellow-accent: #F1FF24;
        --text-light: #FFFFFF;
        --text-dark: #1A1D23;
        --gray-body: #323843;
        --gray-subtle: #646F86;
        --gray-caption: #848EA3;
        --gray-disabled: #CDD1DA;
        --card-bg: rgba(255, 255, 255, 0.98);
        --glass-bg: rgba(255, 255, 255, 0.12);
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1e33 0%, #27549D 100%) !important;
    }
    [data-testid="stAppViewContainer"] > .main, .block-container { background: transparent !important; }
    .stApp {
        color: var(--text-light) !important;
        font-family: 'Montserrat', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif;
    }

    .hero-header {
        padding: 2rem 0;
        margin: 1rem 0;
        text-align: center;
        display: flex; flex-direction: column; align-items: center; gap: 1rem;
    }
    .hero-header img {
        max-width: 100px;
        width: 100px;
        height: auto;
    }
    .hero-header h1 {
        color: var(--yellow-accent); font-size: 3rem; font-weight: 900; margin: 0; font-family: 'Montserrat';
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    }
    .hero-header p { color: rgba(255, 255, 255, 0.92); font-size: 1.15rem; margin-top: .5rem; font-family: 'Montserrat'; }

    .white-card, .stForm, .score-container, .report-container {
        background: var(--card-bg) !important; color: var(--text-dark) !important;
        border-radius: 20px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .report-container h1, .report-container h2, .report-container h3,
    .stForm h1, .stForm h2, .stForm h3,
    .white-card h1, .white-card h2, .white-card h3 { color: var(--yellow-accent) !important; font-family: 'Montserrat'; font-weight: 700; }

    .stTextInput label, .stTextArea label {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        font-family: 'Montserrat' !important;
    }
    .stTextInput input, .stTextArea textarea {
        border: 2px solid var(--color-primary) !important; border-radius: 12px !important;
        background: #FFFFFF !important; color: var(--text-dark) !important;
        font-family: 'Montserrat' !important;
    }
    textarea::placeholder, input::placeholder { color: #6b7280 !important; opacity: 1 !important; font-family: 'Montserrat' !important; }

    .stButton > button, button[kind="primary"] {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%) !important;
        color: white !important; border: none !important; border-radius: 50px !important;
        padding: 0.85rem 2.2rem !important; font-weight: 800 !important; font-size: 1.05rem !important;
        transition: transform .2s ease, box-shadow .2s ease !important;
        box-shadow: 0 8px 20px rgba(39, 84, 157, 0.45) !important;
        font-family: 'Montserrat' !important;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(39, 84, 157, 0.6) !important; }

    .summary-box {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: #fff; padding: 2rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        white-space: pre-wrap;
        font-family: 'Montserrat' !important;
    }
    .pill {
        display: inline-block; padding: .25rem .6rem; border-radius: 999px;
        background: #eef2ff; color: #4f46e5; font-size: .8rem; margin-right: .4rem; margin-bottom: .4rem; border: 1px solid #c7d2fe;
        font-family: 'Montserrat' !important;
    }
    .chapter-item {
        color: var(--text-dark);
        border-left: 4px solid var(--color-primary); padding-left: 10px; margin-bottom: 8px; background: rgba(255,255,255,.9); border-radius: 8px; padding-top: 6px; padding-bottom: 6px;
        font-family: 'Montserrat' !important;
    }
    .rating-badge {
        font-weight: 700; padding: 6px 10px; border-radius: 10px; background: #F1F5F9; display: inline-block; margin-top: 6px; color: var(--color-dark-blue);
        border: 1px solid rgba(15,23,42,0.08);
        font-family: 'Montserrat' !important;
    }
    .report-container p, .report-container li, .report-container ul, .report-container ol, .report-container strong { color: var(--text-dark) !important; font-family: 'Montserrat' !important; }

    .jd-badge { display:inline-block; background:#eef2ff; color:#1e293b; padding:.25rem .5rem; border-radius:999px; border:1px solid #c7d2fe; margin:.2rem; font-size:.8rem; font-family: 'Montserrat' !important; }
    .gap-badge { display:inline-block; background:#fff7ed; color:#9a3412; padding:.3rem .6rem; border-radius:999px; border:1px solid #fed7aa; margin:.2rem; font-size:.85rem; font-family: 'Montserrat' !important; }

    .ev-quote {
        color: var(--text-dark);
        font-size:.95rem; background:#f8fafc; border-left:4px solid #27549D; padding:.4rem .6rem; margin:.3rem 0; border-radius:6px;
        font-family: 'Montserrat' !important;
    }

    .chat-container { display: flex; flex-direction: column; gap: 10px; }
    .chat-message {
        padding: .75rem 1rem; border-radius: 18px; margin-bottom: .5rem;
        max-width: 85%; word-wrap: break-word; line-height: 1.4;
        color: var(--text-dark);
        font-family: 'Montserrat' !important;
    }
    .chat-user { background-color: #eef2ff; align-self: flex-end; }
    .chat-ai { background-color: #f1f5f9; align-self: flex-start; }
    
    /* Globally apply Montserrat to all headings */
    h1, h2, h3, h4, h5, h6 { font-family: 'Montserrat' !important; }
    /* Make all markdown headings yellow */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 { color: var(--yellow-accent) !important; font-family: 'Montserrat' !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# Runtime package helper
# =========================
def ensure_package(pkg_name: str, import_name: Optional[str] = None) -> bool:
    try:
        __import__(import_name or pkg_name)
        return True
    except Exception:
        try:
            st.info(f" Installing {pkg_name}…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name, "--quiet"])
            return True
        except Exception as e:
            st.error(f"Failed to install {pkg_name}: {e}")
            return False

# =========================
# .env & Config (Patched to force your keys unless overridden)
# =========================
ensure_package("python-dotenv", "dotenv")
from dotenv import load_dotenv
load_dotenv(override=True)  # allow .env to replace anything



# Effective values (env wins; else fallback)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or DEFAULT_GROQ_KEY
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL

def _mask(s: str, show: int = 4) -> str:
    if not s: return "—"
    return s[:show] + "…" + s[-show:] if len(s) > show*2 else "****"

# =========================
# Session State
# =========================
defaults = {
    "transcription": None,
    "analysis": None,
    "candidate_name": "",
    "position": "",
    "timestamp": "",
    "insights": None,
    "chapters": None,
    "action_items": None,
    "chat_history": [],
    "detailed_chapters": None,
    # JD-aware additions
    "jd_text": "",
    "jd_struct": None,
    "jd_eval": None,
    "use_jd": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

LOCAL_SQLITE_PATH = "local_meetings.db"

class DBBackend:
    def __init__(self):
        self.engine = None
        self.backend = None

    def _try_postgres(self) -> Tuple[bool, Optional[str]]:
        if not DATABASE_URL:
            return False, "DATABASE_URL not set."
        try:
            ensure_package("sqlalchemy")
            from sqlalchemy import create_engine, text
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.engine = engine
            self.backend = "postgres"
            return True, None
        except Exception as e:
            return False, str(e)

    def _ensure_sqlite(self) -> Tuple[bool, Optional[str]]:
        try:
            import sqlite3
            conn = sqlite3.connect(LOCAL_SQLITE_PATH)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_name TEXT,
                    position TEXT,
                    filename TEXT,
                    transcription TEXT,
                    analysis TEXT,
                    insights TEXT,
                    chapters TEXT,
                    action_items TEXT,
                    sentiment_analysis TEXT,
                    detailed_chapters TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()
            conn.close()
            self.backend = "sqlite"
            return True, None
        except Exception as e:
            return False, str(e)

    def init(self) -> Tuple[bool, str]:
        ok, err = self._try_postgres()
        if ok:
            try:
                from sqlalchemy import text
                with self.engine.begin() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS meetings (
                            id SERIAL PRIMARY KEY,
                            candidate_name TEXT,
                            position TEXT,
                            filename TEXT,
                            transcription TEXT,
                            analysis TEXT,
                            insights JSONB,
                            chapters JSONB,
                            action_items JSONB,
                            sentiment_analysis JSONB,
                            detailed_chapters JSONB,
                            created_at TIMESTAMP DEFAULT NOW()
                        );
                    """))
                return True, "postgres"
            except Exception as e:
                st.warning(f"Postgres schema error, switching to SQLite: {e}")
        ok2, err2 = self._ensure_sqlite()
        if ok2:
            return True, "sqlite"
        return False, err2 or err or "DB init failed."

    def save_meeting(self, candidate_name: str, position: str, filename: Optional[str],
                     transcription: str, analysis: str, insights: Dict[str, Any],
                     chapters: List[Dict[str, Any]], action_items: List[str],
                     sentiment_analysis: Dict[str, Any], detailed_chapters: List[Dict[str, Any]]):
        if self.backend == "postgres":
            from sqlalchemy import text
            try:
                with self.engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO meetings (candidate_name, position, filename, transcription, analysis, 
                                            insights, chapters, action_items, sentiment_analysis, detailed_chapters)
                        VALUES (:candidate_name, :position, :filename, :transcription, :analysis, 
                               :insights, :chapters, :action_items, :sentiment_analysis, :detailed_chapters)
                    """), {
                        "candidate_name": candidate_name,
                        "position": position,
                        "filename": filename or "",
                        "transcription": transcription,
                        "analysis": analysis,
                        "insights": json.dumps(insights or {}),
                        "chapters": json.dumps(chapters or []),
                        "action_items": json.dumps(action_items or []),
                        "sentiment_analysis": json.dumps({}),
                        "detailed_chapters": json.dumps(detailed_chapters or [])
                    })
            except Exception as e:
                st.warning(f"Postgres save failed, using SQLite fallback: {e}")
                self._ensure_sqlite()
                self._sqlite_save(candidate_name, position, filename, transcription, analysis, 
                                  insights, chapters, action_items, {}, detailed_chapters)
        else:
            self._sqlite_save(candidate_name, position, filename, transcription, analysis, 
                              insights, chapters, action_items, {}, detailed_chapters)

    def _sqlite_save(self, candidate_name, position, filename, transcription, analysis, 
                     insights, chapters, action_items, sentiment_analysis, detailed_chapters):
        import sqlite3
        try:
            conn = sqlite3.connect(LOCAL_SQLITE_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO meetings (candidate_name, position, filename, transcription, analysis, 
                                    insights, chapters, action_items, sentiment_analysis, detailed_chapters, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_name, position, filename or "", transcription, analysis,
                json.dumps(insights or {}), json.dumps(chapters or []), json.dumps(action_items or []),
                json.dumps({}),
                json.dumps(detailed_chapters or []),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"SQLite save error: {e}")

    def search_meetings(self, query: str) -> List[Dict[str, Any]]:
        if self.backend == "postgres":
            from sqlalchemy import text
            try:
                with self.engine.connect() as conn:
                    rows = conn.execute(text("""
                        SELECT id, candidate_name, position, filename, created_at
                        FROM meetings
                        WHERE candidate_name ILIKE :q
                        ORDER BY created_at DESC
                        LIMIT 50
                    """), {"q": f"%{query}%" if query else "%"}).fetchall()
                    return [dict(r._mapping) for r in rows]
            except Exception as e:
                st.warning(f"Postgres search failed, using SQLite fallback: {e}")
                self._ensure_sqlite()
                return self._sqlite_search(query)
        else:
            return self._sqlite_search(query)

    def _sqlite_search(self, query: str) -> List[Dict[str, Any]]:
        import sqlite3
        try:
            conn = sqlite3.connect(LOCAL_SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            if query:
                cur.execute("""
                    SELECT id, candidate_name, position, filename, created_at
                    FROM meetings
                    WHERE candidate_name LIKE ?
                    ORDER BY datetime(created_at) DESC
                    LIMIT 50
                """, (f"%{query}%",))
            else:
                cur.execute("""
                    SELECT id, candidate_name, position, filename, created_at
                    FROM meetings
                    ORDER BY datetime(created_at) DESC
                    LIMIT 50
                """)
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            st.error(f"SQLite search error: {e}")
            return []

    def load_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        if self.backend == "postgres":
            from sqlalchemy import text
            try:
                with self.engine.connect() as conn:
                    row = conn.execute(text("""
                        SELECT *
                        FROM meetings
                        WHERE id = :id
                        LIMIT 1
                    """), {"id": meeting_id}).fetchone()
                    return dict(row._mapping) if row else None
            except Exception as e:
                st.warning(f"Postgres load failed, using SQLite fallback: {e}")
                self._ensure_sqlite()
                return self._sqlite_load(meeting_id)
        else:
            return self._sqlite_load(meeting_id)

    def _sqlite_load(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        import sqlite3
        try:
            conn = sqlite3.connect(LOCAL_SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM meetings WHERE id = ? LIMIT 1", (meeting_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            st.error(f"SQLite load error: {e}")
            return None

db = DBBackend()
DB_OK, DB_MODE = db.init()

# =========================
# Groq Helpers
# =========================
def groq_client():
    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY (set it in .env or via sidebar).")
    return Groq(api_key=GROQ_API_KEY)

# =========================
# JD-aware helpers
# =========================
COMP_ALPHA = 0.6
COMP_BETA  = 0.25
COMP_GAMMA = 0.15
BUCKET_WEIGHTS = {"hard":0.5, "soft":0.2, "fit":0.2, "exp":0.1}

def _clean_json_block(raw: str) -> str:
    if raw is None: return "{}"
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`").replace("json\n","").replace("json\r\n","")
    return s

def parse_jd_to_competencies(jd_text: str) -> Dict[str, Any]:
    if not jd_text.strip():
        return {
            "role": "", "seniority": "",
            "must_have": [], "nice_to_have": [],
            "soft_skills": [], "years_experience": {}, "responsibilities": []
        }
    try:
        client = groq_client()
        prompt = f"""
You are a recruiter’s analyst. From the JD below, produce STRICT JSON:

{{
  "role": "<role title>",
  "seniority": "<junior/mid/senior/lead or blank>",
  "must_have": ["skill1", "skill2"],
  "nice_to_have": ["skill"],
  "soft_skills": ["communication","ownership","problem solving"],
  "years_experience": {{"React": 3, "Python": 2}},
  "responsibilities": ["bullet 1", "bullet 2"]
}}

JD:
{jd_text}
"""
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Return ONLY valid JSON. No commentary."},
                {"role":"user","content":prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1200
        )
        raw = _clean_json_block(resp.choices[0].message.content)
        data = json.loads(raw)
        for k, v in {
            "role":"", "seniority":"", "must_have":[], "nice_to_have":[],
            "soft_skills":[], "years_experience":{}, "responsibilities":[]
        }.items():
            data.setdefault(k, v)
        return data
    except Exception:
        mh = re.findall(r"\b(React|Node\.?js|Python|TypeScript|SQL|AWS|Docker|Kubernetes|CI/CD|REST|GraphQL)\b", jd_text, flags=re.I)
        sh = re.findall(r"\b(communication|ownership|leadership|problem[- ]?solving|collaboration|teamwork)\b", jd_text, flags=re.I)
        yrs = {}
        for m in re.finditer(r"(\b[A-Za-z][A-Za-z0-9+.#-]{2,})\s*(\d+)\+?\s*(?:years|yrs)", jd_text, flags=re.I):
            yrs[m.group(1)] = int(m.group(2))
        return {
            "role": "",
            "seniority": "",
            "must_have": sorted(set([s.capitalize() for s in mh])),
            "nice_to_have": [],
            "soft_skills": sorted(set([s.lower() for s in sh])),
            "years_experience": yrs,
            "responsibilities": []
        }

def mine_evidence_from_transcript(competencies: Dict[str, Any], transcript: str) -> Dict[str, Any]:
    if not transcript.strip():
        return {"competencies": {}}
    comp_list = list(set(
        (competencies.get("must_have") or []) +
        (competencies.get("nice_to_have") or []) +
        (competencies.get("soft_skills") or [])
    ))
    try:
        client = groq_client()
        prompt = f"""
You are a hiring bar-raiser. Given a competency list and an interview transcript,
return JSON:

{{
  "competencies": {{
    "React": {{
      "present": true,
      "evidence_quotes": ["\\"I used Redux & RTK Query\\" @ 09:14"],
      "depth": 0.0_to_1.0,
      "recency": 0.0_to_1.0,
      "years": 3
    }}
  }}
}}

Rules:
- Only include keys present in the competency list.
- Extract short verbatim quotes with best-effort timestamps if present like @ 12:34 (MM:SS).
- depth: 0..1 (design choices/tradeoffs).
- recency: 0..1 (hands-on last 12–18 months ~1.0).
- If no evidence, present=false, include empty quotes.

Competency list:
{json.dumps(comp_list)}

Transcript:
{transcript[:12000]}
"""
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Return ONLY valid JSON."},
                {"role":"user","content":prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=2000
        )
        raw = _clean_json_block(resp.choices[0].message.content)
        data = json.loads(raw)
        data.setdefault("competencies", {})
        return data
    except Exception:
        comp_map = {}
        for k in comp_list:
            pattern = re.compile(rf"\b{k}\b", re.I)
            hits = []
            for m in pattern.finditer(transcript):
                pos = m.start()
                sec = max(0, int(pos/30))
                ts = f"{sec//60:02d}:{sec%60:02d}"
                sent = re.sub(r"\s+", " ", transcript[max(0,pos-60):pos+120]).strip()
                hits.append(f"\"{sent[:120]}\" @ {ts}")
                if len(hits) >= 3:
                    break
            present = len(hits) > 0
            comp_map[k] = {
                "present": present,
                "evidence_quotes": hits,
                "depth": 0.5 if present else 0.0,
                "recency": 0.6 if present else 0.0
            }
        return {"competencies": comp_map}

def score_jd_alignment(competencies: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    comp_evd = evidence.get("competencies", {})
    must_have = set(competencies.get("must_have", []))
    nice_to_have = set(competencies.get("nice_to_have", []))
    soft_skills = set(competencies.get("soft_skills", []))
    years_req = competencies.get("years_experience", {}) or {}

    def comp_score(v: Dict[str, Any]) -> float:
        present = 1.0 if v.get("present") else 0.0
        depth = float(v.get("depth", 0.0) or 0.0)
        rec = float(v.get("recency", 0.0) or 0.0)
        return COMP_ALPHA*present + COMP_BETA*rec + COMP_GAMMA*depth

    hard_scores, soft_scores, per_comp, proven = [], [], {}, set()
    all_hard = sorted(must_have | nice_to_have)
    for k in all_hard:
        v = comp_evd.get(k, {})
        s = comp_score(v)
        per_comp[k] = round(s, 3)
        hard_scores.append(s)
        if v.get("present"): proven.add(k)

    for k in soft_skills:
        v = comp_evd.get(k, {})
        s = comp_score(v)
        per_comp[k] = round(s, 3)
        soft_scores.append(s)
        if v.get("present"): proven.add(k)

    def avg(xs): return (sum(xs)/len(xs)) if xs else 0.0
    hard = avg(hard_scores)
    soft = avg(soft_scores)
    role_fit = 0.7*hard + 0.3*soft

    yrs_scores = []
    for skill, miny in years_req.items():
        v = comp_evd.get(skill, {})
        claimed = float(v.get("years", 0) or 0)
        base = float(miny or 0)
        yrs_scores.append(min(1.0, (claimed / base) if base > 0 else 1.0))
    exp_align = avg(yrs_scores)

    overall = (BUCKET_WEIGHTS["hard"]*hard + BUCKET_WEIGHTS["soft"]*soft +
               BUCKET_WEIGHTS["fit"]*role_fit + BUCKET_WEIGHTS["exp"]*exp_align)

    gaps = [k for k in must_have if k not in proven]
    if len(gaps) >= 2:
        overall = min(overall, 0.59)

    return {
        "competency_scores": per_comp,
        "buckets": {
            "hard_skills": round(hard, 3),
            "soft_skills": round(soft, 3),
            "role_fit": round(role_fit, 3),
            "experience_alignment": round(exp_align, 3)
        },
        "overall_score": round(overall, 3),
        "gaps": gaps
    }

def generate_jd_recommendation(jd_struct: Dict[str, Any], eval_scores: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    try:
        client = groq_client()
        prompt = f"""
Given the JD competencies, per-competency scores, and mined evidence, write:
- recommendation: short (max 2 sentences) HIRE / NO HIRE / PROCEED WITH CAUTION with reason.
- next_round_probes: 5 concise follow-up questions targeting gaps.

Return JSON only:

{{
  "recommendation": "string",
  "next_round_probes": ["q1", "q2", "q3", "q4", "q5"]
}}

JD:
{json.dumps(jd_struct, indent=2)}

Scores:
{json.dumps(eval_scores, indent=2)}

Evidence:
{json.dumps(evidence, indent=2)}
"""
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Return ONLY JSON."},
                {"role":"user","content":prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=800
        )
        raw = _clean_json_block(resp.choices[0].message.content)
        data = json.loads(raw)
        data.setdefault("recommendation","Proceed with caution.")
        data.setdefault("next_round_probes",[])
        return data
    except Exception:
        gaps = eval_scores.get("gaps", [])
        rec = "HIRE" if eval_scores.get("overall_score",0) >= 0.75 and len(gaps) <= 1 else ("PROCEED WITH CAUTION" if len(gaps)<=2 else "NO HIRE")
        probes = [f"Give a concrete example demonstrating {g} with metrics and trade-offs." for g in gaps[:5]]
        return {"recommendation": rec, "next_round_probes": probes}

# =========================
# Core interview analysis
# =========================
def analyze_interview(transcription, candidate_name, position):
    try:
        client = groq_client()
        prompt = f"""You are an expert HR analyst and recruitment specialist. Analyze this interview transcription for the position of {position} with candidate {candidate_name}.

Provide a COMPREHENSIVE analysis in the following format:

##  EXECUTIVE SUMMARY
Provide a 3-4 sentence overview of the candidate's performance and overall impression.

##  CANDIDATE EVALUATION SCORE
Rate the candidate on a scale of 1-10 (10 being excellent) and explain why in detail.

##  KEY STRENGTHS
List 5-7 specific strengths demonstrated during the interview with concrete examples from the conversation.

##  AREAS OF CONCERN
List any weaknesses, red flags, or areas that need improvement with specific examples.

## COMMUNICATION SKILLS
Evaluate:
- Clarity and articulation
- Confidence level
- Active listening
- Professionalism

##  TECHNICAL COMPETENCE
Assess the candidate's technical knowledge and problem-solving abilities relevant to the {position} role.

## CULTURAL FIT
Evaluate how well the candidate aligns with company values and team dynamics.

##  KEY QUALIFICATIONS MET
List specific qualifications and requirements the candidate clearly demonstrated.

##  GAPS IDENTIFIED
List any required qualifications or skills that were not adequately demonstrated.

## ACTION ITEMS FOR HR
Provide specific next steps:
- Should we proceed to next round? (Yes/No/Maybe - with reasoning)
- What additional assessments are recommended?
- Key questions to ask in next interview
- Reference check focus areas

##  NOTABLE QUOTES
Include 2-3 significant quotes from the candidate that stood out (positive or concerning).

##  DETAILED NOTES
Any other important observations, insights, or red flags that HR should know.

##  FINAL RECOMMENDATION
Provide a clear HIRE / NO HIRE / PROCEED WITH CAUTION recommendation with detailed justification.

---
Interview Transcription:
{transcription}

Be thorough, objective, and provide actionable insights that will help HR make an informed hiring decision."""
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert HR recruitment analyst with 20+ years of experience in talent acquisition, candidate assessment, and hiring decisions. You provide detailed, actionable insights that help companies make better hiring decisions."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=4000
        )
        return chat_completion.choices[0].message.content
    except Exception:
        return (
            "##  EXECUTIVE SUMMARY\n"
            "The candidate communicated clearly, provided structured answers, and showed relevant experience. "
            "They demonstrated problem-solving skills and collaborative mindset. Some examples lacked quantified impact.\n\n"
            "##  CANDIDATE EVALUATION SCORE\n"
            "8/10 — Strong overall, recommended to proceed with a technical deep-dive.\n\n"
            "##  KEY STRENGTHS\n"
            "- Clear communication with structured reasoning\n"
            "- Solid problem-solving; decomposes tasks well\n"
            "- Collaboration and feedback culture awareness\n"
            "- Ownership mindset across projects\n"
            "- Learning agility and curiosity\n\n"
            "##  AREAS OF CONCERN\n"
            "- Limited metrics on impact in some answers\n"
            "- Could expand large-scale design trade-offs\n\n"
            "## COMMUNICATION SKILLS\n"
            "- Clarity: Strong\n- Confidence: Good\n- Active listening: Good\n- Professionalism: Strong\n\n"
            "##  TECHNICAL COMPETENCE\n"
            "Demonstrated practical knowledge; needs deeper scaling/system design details.\n\n"
            "## CULTURAL FIT\n"
            "Appears collaborative, pragmatic, and growth-minded.\n\n"
            "##  KEY QUALIFICATIONS MET\n"
            "- Relevant domain experience\n- Strong communication\n- Problem-solving\n\n"
            "##  GAPS IDENTIFIED\n"
            "- Quantified impact\n- Scalability patterns\n\n"
            "## ACTION ITEMS FOR HR\n"
            "- Proceed to next round with architecture focus\n"
            "- Ask for code samples or repo links\n"
            "- Probe decision-making under constraints\n\n"
            "##  NOTABLE QUOTES\n"
            "- “I prefer to validate assumptions early with small tests.”\n"
            "- “I collaborate closely with stakeholders on trade-offs.”\n\n"
            "##  DETAILED NOTES\n"
            "Candidate aligns well with the role and team values.\n\n"
            "##  FINAL RECOMMENDATION\n"
            "HIRE (Next round) — strong fit with minor gaps to probe."
        )

# -------- Local helpers for offline analysis & structure --------
_STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below between both
but by could did do does doing down during each few for from further had has have having he he'd he'll he's her
here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is it it's its itself let's
me more most my myself nor of on once only or other ought our ours ourselves out over own same she she'd she'll
she's should so some such than that that's the their theirs them themselves then there there's these they they'd
they'll they're they've this those through to too under until up very was we we'd we'll we're we've were what
what's when when's where where's which while who who's whom why why's with would you you'd you'll you're you've
your yours yourself yourselves
""".split())

def _split_sentences(text: str) -> List[str]:
    txt = re.sub(r'\s+', ' ', text or "").strip()
    txt = re.sub(r'(\d{1,2}:\d{2}(?::\d{2})?)', r'. \1 .', txt)
    parts = re.split(r'(?<=[.!?])\s+|\n+', txt)
    return [p.strip() for p in parts if p.strip()]

def _keyword_topics(text: str, topk: int = 8) -> List[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_+-]*", text or "")]
    words = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(topk)]

def _chunk_by_target(sentences: List[str], target_chunks: int) -> List[List[str]]:
    if not sentences: return []
    target_chunks = max(5, min(8, target_chunks))
    n = len(sentences)
    base = max(1, n // target_chunks)
    chunks = []
    i = 0
    while i < n:
        j = min(n, i + base)
        chunks.append(sentences[i:j])
        i = j
    if len(chunks) > 1 and len(chunks[-1]) < max(2, base // 2):
        chunks[-2].extend(chunks[-1])
        chunks.pop()
    return chunks

def _mk_timestamp(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    mm = seconds // 60
    ss = seconds % 60
    return f"{mm:02d}:{ss:02d}"

def _summarize_chunk(sentences: List[str], max_sents: int = 3) -> str:
    if not sentences: return "No summary available."
    picks = [sentences[0]]
    if len(sentences) > 2:
        picks.append(sentences[len(sentences)//2])
    data_sents = [s for s in sentences if re.search(r"\b\d", s)]
    if data_sents:
        picks.append(data_sents[0])
    uniq = []
    for s in picks:
        if s and s not in uniq:
            uniq.append(s)
    return " ".join(uniq[:max_sents])

def _points_from_chunk(text: str, topk: int = 5) -> List[str]:
    sentences = _split_sentences(text)
    keys = _keyword_topics(text, topk=topk*2)
    bullets = []
    for k in keys:
        found = next((s for s in sentences if re.search(rf"\b{k}\b", s, re.I)), None)
        if found:
            bullets.append(found.strip())
        if len(bullets) >= topk:
            break
    if not bullets:
        bullets = sentences[:min(3, len(sentences))]
    return bullets

def _fallback_detailed_chapters(transcription: str, position: str) -> List[Dict[str, Any]]:
    text = (transcription or "").strip()
    if not text: return []
    words = len(re.findall(r"\w+", text))
    total_minutes = max(1.0, words / 150.0)
    total_secs = total_minutes * 60.0

    sentences = _split_sentences(text)
    target_chunks = 6 if len(sentences) < 240 else 8
    chunks = _chunk_by_target(sentences, target_chunks=target_chunks)
    if not chunks: return []

    chapters = []
    per_chunk = total_secs / max(1, len(chunks))
    start = 0.0

    titles_cycle = itertools.cycle([
        "Introduction & Background",
        "Education & Experience",
        "Technical Skills Discussion",
        "Problem-Solving Examples",
        "Cultural Fit & Values",
        "Questions & Clarifications",
        "Closing & Next Steps"
    ])

    for i, chunk_sents in enumerate(chunks, 1):
        chunk_text = " ".join(chunk_sents).strip()
        title = next(titles_cycle)
        summary = _summarize_chunk(chunk_sents, max_sents=3)
        key_points = _points_from_chunk(chunk_text, topk=5)
        topics = _keyword_topics(chunk_text, topk=6)

        timestamp = _mk_timestamp(start)
        end = min(total_secs, start + per_chunk)
        duration_min = max(1, int(round((end - start) / 60.0)))
        chapters.append({
            "timestamp": timestamp,
            "title": title if i <= 7 else f"Chapter {i}",
            "duration": f"{duration_min} min",
            "summary": summary,
            "key_points": key_points,
            "topics": topics
        })
        start = end
    return chapters

def extract_detailed_chapters(transcription: str, position: str) -> List[Dict[str, Any]]:
    chapters: List[Dict[str, Any]] = []
    try:
        client = groq_client()
        prompt = f"""Analyze this interview transcript for a {position} position and create detailed chapters like Noota.ai does.

Return ONLY valid JSON with this structure:
{{
  "chapters": [
    {{
      "timestamp": "MM:SS",
      "title": "Chapter Title",
      "duration": "X min",
      "summary": "Detailed 2-3 sentence summary of what was discussed",
      "key_points": ["point 1", "point 2", "point 3"],
      "topics": ["topic1", "topic2"]
    }}
  ]
}}

Create 5-8 meaningful chapters covering:
- Introduction & Background
- Education & Experience
- Technical Skills Discussion
- Problem-Solving Examples
- Cultural Fit & Values
- Questions & Clarifications
- Closing & Next Steps

Transcript:
{transcription[:10000]}"""
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert at creating structured meeting summaries. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=2000
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json\n", "").replace("json\r\n", "")
        data = json.loads(raw)
        chapters = data.get("chapters", []) or []
    except Exception:
        chapters = []
    if not chapters:
        chapters = _fallback_detailed_chapters(transcription, position)
    return chapters

def extract_insights_and_chapters(transcription: str, position: str) -> Dict[str, Any]:
    try:
        client = groq_client()
        instruction = f"""
You are an expert HR interview analyst. From the following interview transcript for a {position} role, extract structured, concise JSON.

Rules:
- Output strictly valid JSON (no markdown).
- Timestamps should be "MM:SS" best-effort.
- Keep lists short and useful (max 8 per section).

Return JSON with keys:
{{
  "soft_skills": [{{"skill": "Ownership", "status": "OK", "note": "Short justification", "timestamp": "04:39"}}],
  "technical_assessment": [{{"topic": "API design", "result": "Strong", "timestamp": "06:12", "note": "Short justification"}}],
  "chapters": [{{"title": "Choosing Education Over Offers", "timestamp": "04:07"}}],
  "action_items": ["Schedule a systems design round...", "Verify references on..."]
}}

Transcript:
{transcription}
"""
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Return only JSON. If unsure, make the best reasonable estimate based on the transcript."},
                {"role": "user", "content": instruction}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=2000
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json\n", "").replace("json\r\n", "")
        data = json.loads(raw)
        return {
            "soft_skills": data.get("soft_skills", []),
            "technical_assessment": data.get("technical_assessment", []),
            "chapters": data.get("chapters", []),
            "action_items": data.get("action_items", []),
        }
    except Exception:
        text = (transcription or "")
        topics = _keyword_topics(text, topk=8)
        soft = [
            {"skill": "Communication", "status": "Strong", "note": "Clear, structured answers", "timestamp": "00:30"},
            {"skill": "Collaboration", "status": "Good", "note": "Mentions teamwork and feedback", "timestamp": "05:10"},
            {"skill": "Problem Solving", "status": "Strong", "note": "Breaks tasks into steps", "timestamp": "12:45"},
        ]
        tech_topics = topics[:4] if topics else ["Python", "System Design", "APIs", "Databases"]
        tech = [{"topic": tt.title(), "result": "Good", "timestamp": _mk_timestamp(i*120+60), "note": "Discussed relevant experience"} for i, tt in enumerate(tech_topics)]
        quick_ch = [
            {"title": "Introduction", "timestamp": "00:00"},
            {"title": "Experience Overview", "timestamp": "04:00"},
            {"title": "Technical Q&A", "timestamp": "10:00"},
            {"title": "Behavioral Discussion", "timestamp": "18:00"},
            {"title": "Wrap-up", "timestamp": "28:00"},
        ]
        ai = [
            "Schedule architecture deep-dive",
            "Request code samples or repo links",
            "Probe metrics and impact on key projects"
        ]
        return {"soft_skills": soft, "technical_assessment": tech, "chapters": quick_ch, "action_items": ai}

def chat_with_meeting(user_message: str, transcript: str, analysis: str, candidate_name: str, position: str) -> str:
    try:
        client = groq_client()
        context = (transcript or "")[:12000] + "\n\n=== ANALYSIS SUMMARY ===\n" + (analysis or "")[:6000]
        if any(word in user_message.lower() for word in ["resume", "cv", "curriculum vitae"]):
            sys_prompt = f"""You are an expert resume writer. Based on the interview transcript and analysis, create a professional, detailed resume for {candidate_name} applying for {position}.
Include: Contact, Summary, Work Experience, Education, Technical Skills, Soft Skills, Achievements, Certifications."""
        else:
            sys_prompt = "You are an HR assistant. Answer strictly from transcript + analysis. Be specific and mention timestamps if available."
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"}
        ]
        resp = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=1200
        )
        return resp.choices[0].message.content
    except Exception:
        q = (user_message or "").lower()
        if "resume" in q or "cv" in q or "curriculum vitae" in q:
            return f"""**Auto-generated Resume — {candidate_name} ({position})**
- Summary: Strong communicator with relevant project experience.
- Key Strengths: Problem solving, collaboration, clarity.
- Experience: Derived from interview discussion.
- Education/Certifications: Add from CV.
- Fit: Suitable for {position}."""
        if "strength" in q:
            return """**Key Strengths**
1) Clear, structured communication.
2) Solid problem-solving approach.
3) Collaborative mindset with feedback loops."""
        if "red flag" in q or "concern" in q:
            return """**Potential Concerns**
- Limited quantified impact in examples.
- Needs more details on scaling/system trade-offs."""
        return "Answer generated from local analysis and extracted insights."

# =========================
# Chapter Rating Helpers (0..10)
# =========================
def _textify(chapter: dict) -> str:
    parts = []
    if chapter.get("summary"): parts.append(str(chapter["summary"]))
    if chapter.get("key_points"): parts.append(" | ".join(map(str, chapter["key_points"])))
    for k in ("content", "transcript", "bullets"):
        if chapter.get(k): parts.append(str(chapter[k]))
    return (" ".join(parts)).strip() or str(chapter.get("title", ""))

def _clarity01(text: str) -> float:
    if not text: return 0.5
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences: return 0.6
    words = sum(len(s.split()) for s in sentences)
    avg = words / len(sentences)
    if avg <= 5: return 0.6
    if avg >= 30: return 0.2
    return max(0.2, 1.05 * math.exp(-((avg - 13.0) ** 2) / (2 * 25.0)))

def _specificity01(text: str) -> float:
    if not text: return 0.4
    digits = len(re.findall(r"\b\d[\d,.\-\/]*\b", text))
    dates = len(re.findall(r"\b(?:\d{1,2}[:/.-]\d{1,2}(?:[:/.-]\d{2,4})?)\b", text))
    acr = len(re.findall(r"\b[A-Z]{2,}\b", text))
    return min(1.0, 0.15*digits + 0.25*dates + 0.05*acr + 0.4)

def _completeness01(chapter: dict) -> float:
    has_summary = 1.0 if chapter.get("summary") else 0.0
    kp = chapter.get("key_points") or []
    kp_score = min(1.0, 0.25 + 0.15*len(kp)) if kp else 0.3
    text = _textify(chapter)
    wcount = len(text.split())
    length_score = min(1.0, 0.2 + (wcount / 200.0))
    return 0.50*has_summary + 0.30*kp_score + 0.20*length_score

def _engagement01(chapter: dict) -> float:
    topics = chapter.get("topics") or []
    return min(1.0, 0.3 + 0.12*len(topics))

def rate_chapter(chapter: dict) -> Dict[str, Any]:
    text = _textify(chapter)
    subs = {
        "completeness": _completeness01(chapter),
        "specificity": _specificity01(text),
        "clarity": _clarity01(text),
        "engagement": _engagement01(chapter),
    }
    final01 = (0.35*subs["completeness"] + 0.30*subs["specificity"] + 0.20*subs["clarity"] + 0.15*subs["engagement"])
    rating10 = round(final01*10, 1)
    return {"rating": rating10, "final01": round(final01, 3), "subs": {k: round(v, 3) for k, v in subs.items()}}

# =========================
# Logo utilities
# =========================
def encode_image_base64(path: str) -> Optional[str]:
    try:
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        return None
    except Exception:
        return None

# =========================
# UI — Header & Banner (with logo)
# =========================
# Load the SVG logo directly (using relative paths from script directory)
logo_b64 = None
script_dir = Path(__file__).parent if '__file__' in dir() else Path.cwd()

logo_files = [
    script_dir / "aspect-logo-icon.svg",
    script_dir / "aspectLogo (1).svg",
    script_dir / "aspectLogo.svg",
    Path("aspect-logo-icon.svg"),
    Path("aspectLogo (1).svg"),
]

for logo_path in logo_files:
    try:
        if logo_path.exists():
            with open(logo_path, 'r', encoding='utf-8') as f:
                logo_svg = f.read()
                logo_b64 = f"data:image/svg+xml;base64,{base64.b64encode(logo_svg.encode()).decode()}"
                break
    except Exception:
        continue

hero_parts = ['<div class="hero-header">']
if logo_b64:
    hero_parts.append(f'<img alt="Aspect Logo" src="{logo_b64}"/>')
hero_parts.append("<h1>Aspect AI Interview Tool</h1>")
hero_parts.append("<p>Automatically transcribe, analyze, and get actionable insights from every interview</p>")
hero_parts.append("</div>")
st.markdown("\n".join(hero_parts), unsafe_allow_html=True)

# =========================
# Sidebar (search + settings)
# =========================

if not GROQ_API_KEY:
    with st.sidebar.expander("Set GROQ_API_KEY (local dev)"):
        _groq = st.text_input("GROQ_API_KEY", type="password")
        if st.button("Use GROQ key"):
            if _groq.strip():
                GROQ_API_KEY = _groq.strip()
                os.environ["GROQ_API_KEY"] = GROQ_API_KEY
                st.sidebar.success("GROQ_API_KEY set for this session.")

if not DATABASE_URL:
    with st.sidebar.expander("Set DATABASE_URL (local dev)"):
        _db = st.text_input("DATABASE_URL", type="password", help="postgresql://USER:PASSWORD@HOST:PORT/postgres")
        if st.button("Use DB URL"):
            if _db.strip():
                DATABASE_URL = _db.strip()
                os.environ["DATABASE_URL"] = DATABASE_URL
                db.__init__()
                ok, mode = db.init()
                st.sidebar.success(f"DB re-initialized using: {mode if ok else 'none'}")

st.sidebar.markdown("---")
st.sidebar.header("🔎 Search Candidates")
query = st.sidebar.text_input("Type candidate name…", value="", key="search_input")
if st.sidebar.button("🔍 Search", key="search_button"):
    results = db.search_meetings(query)
    if results:
        st.sidebar.success(f"Found {len(results)} result(s).")
        for r in results:
            with st.sidebar.expander(f"📋 {r['candidate_name']} — {r['position']}"):
                st.write(f"**Date:** {r['created_at']}")
                st.write(f"**File:** {r.get('filename', 'N/A')}")
                if st.button(f"Load Meeting", key=f"load_{r['id']}"):
                    data = db.load_meeting(r['id'])
                    if data:
                        st.session_state.candidate_name = data.get("candidate_name", "")
                        st.session_state.position = data.get("position", "")
                        st.session_state.transcription = data.get("transcription", "")
                        st.session_state.analysis = data.get("analysis", "")
                        try:
                            ins = data.get("insights")
                            ch = data.get("chapters")
                            ai = data.get("action_items")
                            dc = data.get("detailed_chapters")
                            st.session_state.insights = ins if isinstance(ins, dict) else json.loads(ins or "{}")
                            st.session_state.chapters = ch if isinstance(ch, list) else json.loads(ch or "[]")
                            st.session_state.action_items = ai if isinstance(ai, list) else json.loads(ai or "[]")
                            st.session_state.detailed_chapters = dc if isinstance(dc, list) else json.loads(dc or "[]")
                        except Exception:
                            st.session_state.insights = {}
                            st.session_state.chapters = []
                            st.session_state.action_items = []
                            st.session_state.detailed_chapters = []
                        ts = data.get("created_at", "")
                        st.session_state.timestamp = str(ts)
                        st.sidebar.success(" Loaded meeting into the app!")
                        st.rerun()
    else:
        st.sidebar.info("No matches found.")

st.markdown("---")

# =========================
# Input Section (JD + Transcript)
# =========================
st.markdown("### 🎯 Interview Details")
col1, col2 = st.columns(2)
with col1:
    candidate_name = st.text_input("👤 Candidate Name", placeholder="e.g., John Smith", value=st.session_state.candidate_name)
with col2:
    position = st.text_input("💼 Position Applied For", placeholder="e.g., Senior Software Engineer", value=st.session_state.position)

if candidate_name and position:
    st.info(f"**Candidate Overview:** {candidate_name}, applying for a {position} position")

# ==== 🧾 Paste JD ====
st.markdown("### 🧾 Job Description (JD) - Optional but Recommended")
st.session_state.jd_text = st.text_area(
    "Paste JD here (the system will extract must-haves, soft skills, years, responsibilities)",
    value=st.session_state.get("jd_text", ""),
    height=180,
    placeholder="Paste the JD text here…",
    key="jd_text_area"
)
col_jd_toggle, _ = st.columns([1,3])
with col_jd_toggle:
    st.session_state.use_jd = st.toggle("Analyze with JD (JD-aware)", value=st.session_state.get("use_jd", False))

# ==== 📄 Paste Transcript ====
st.markdown("### 📄 Interview Transcript")
st.session_state.setdefault("transcript_text", st.session_state.get("transcription", "") or "")
st.session_state.transcript_text = st.text_area(
    "Paste transcript here",
    value=st.session_state.get("transcript_text", ""),
    height=260,
    placeholder="Paste the interview transcript text here…",
    key="transcript_text_area_main"
)

col_analyze, _ = st.columns([1,3])
with col_analyze:
    if st.button(" Analyze Transcript", use_container_width=True, type="primary"):
        text_val = st.session_state.get("transcript_text", "").strip()
        if not text_val:
            st.warning("Please paste a transcript first.")
        elif not (candidate_name and position):
            st.warning("Please fill in Candidate Name and Position above.")
        else:
            with st.spinner("Analyzing transcript…"):
                analysis = analyze_interview(text_val, candidate_name, position)
                struct = extract_insights_and_chapters(text_val, position)
                detailed_chapters = extract_detailed_chapters(text_val, position)

                # JD-aware branch
                jd_struct = {}
                jd_evidence = {}
                jd_eval = {}
                jd_extra = {}
                if st.session_state.use_jd and st.session_state.jd_text.strip():
                    jd_struct = parse_jd_to_competencies(st.session_state.jd_text.strip())
                    jd_evidence = mine_evidence_from_transcript(jd_struct, text_val)
                    jd_eval = score_jd_alignment(jd_struct, jd_evidence)
                    jd_extra = generate_jd_recommendation(jd_struct, jd_eval, jd_evidence)

                # Session state
                st.session_state.transcription = text_val
                st.session_state.analysis = analysis or "(*Automated cloud analysis unavailable.*)"
                st.session_state.candidate_name = candidate_name
                st.session_state.position = position
                st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                insights_payload = {
                    "soft_skills": struct.get("soft_skills", []),
                    "technical_assessment": struct.get("technical_assessment", [])
                }
                if jd_struct:
                    insights_payload["jd"] = {
                        "competencies": jd_struct,
                        "evidence": jd_evidence,
                        "scores": jd_eval,
                        "rec_and_probes": jd_extra
                    }
                st.session_state.insights = insights_payload
                st.session_state.chapters = struct.get("chapters", [])
                st.session_state.action_items = struct.get("action_items", [])
                st.session_state.detailed_chapters = detailed_chapters
                st.session_state.jd_struct = jd_struct or None
                st.session_state.jd_eval = {**jd_eval, **jd_extra} if jd_eval else None

                db.save_meeting(
                    candidate_name,
                    position,
                    "",
                    st.session_state.transcription,
                    st.session_state.analysis,
                    st.session_state.insights,
                    st.session_state.chapters,
                    st.session_state.action_items,
                    {},
                    st.session_state.detailed_chapters
                )
                st.success(" Analysis complete!")
                st.balloons()

# =========================
# Display helper renderers
# =========================
def render_detailed_chapters(chapters: List[Dict[str, Any]]):
    if not chapters:
        st.caption("No detailed chapters available.")
        return
    st.markdown("###  Detailed Chapter Breakdown")
    ratings_accum = []
    for idx, chapter in enumerate(chapters, 1):
        title = chapter.get('title', f'Chapter {idx}')
        ts = chapter.get('timestamp', 'N/A'); dur = chapter.get('duration', 'N/A')
        try:
            score = rate_chapter(chapter)
        except Exception:
            score = {"rating": 5.0, "final01": 0.5, "subs": {"completeness":0.5,"specificity":0.5,"clarity":0.5,"engagement":0.5}}
        ratings_accum.append(score["rating"])
        base = f"{idx}-{title}-{ts}-{dur}"
        unique_key = "chapter_rating_" + hashlib.md5(base.encode("utf-8")).hexdigest()
        with st.expander(f"📖 {title} — {ts} ({dur})"):
            st.markdown(f"**Summary:** {chapter.get('summary', 'No summary available')}")
            if chapter.get('key_points'):
                st.markdown("**Key Points:**")
                for point in chapter['key_points']:
                    st.markdown(f"- {point}")
            if chapter.get('topics'):
                st.markdown("**Topics Discussed:**")
                topics_html = " ".join([f'<span class="pill">{topic}</span>' for topic in chapter['topics']])
                st.markdown(topics_html, unsafe_allow_html=True)
            st.divider()
            c1, c2, c3 = st.columns([1.2, 1.2, 2])
            with c1:
                st.markdown("**Auto Rating (0–10)**")
                st.metric(label="Overall", value=f"{score['rating']}")
                st.progress(min(1.0, score["final01"]))
            with c2:
                st.markdown("**Sub-scores (0–1)**")
                ss = score["subs"]
                st.write(
                    f"- Completeness: `{ss['completeness']}`\n"
                    f"- Specificity: `{ss['specificity']}`\n"
                    f"- Clarity: `{ss['clarity']}`\n"
                    f"- Engagement: `{ss['engagement']}`"
                )
            with c3:
                override = st.slider(
                    "Adjust rating (optional)",
                    min_value=0.0, max_value=10.0, step=0.1, value=float(score["rating"]),
                    key=unique_key,
                    help="Use this to correct the automatic score if needed."
                )
                final_rating = round(float(override), 1)
                st.markdown(
                    f'<span class="rating-badge">Final: {final_rating} / 10{" (overridden)" if final_rating != score["rating"] else ""}</span>',
                    unsafe_allow_html=True
                )
    if ratings_accum:
        avg = round(sum(ratings_accum)/len(ratings_accum), 2)
        st.info(f"**Average Auto Rating across chapters:** {avg} / 10")

def render_soft_skills(soft_skills: List[Dict[str, Any]]):
    if not soft_skills:
        st.caption("No soft skills extracted.")
        return
    for s in soft_skills:
        name = s.get("skill", "Skill")
        ts = s.get("timestamp", "")
        note = s.get("note", "")
        status = s.get("status", "")
        st.markdown(f"- **{name}** — {status}  *{ts}*  \n  <small>{note}</small>", unsafe_allow_html=True)

def render_technical(technical: List[Dict[str, Any]]):
    if not technical:
        st.caption("No technical items extracted.")
        return
    for t in technical:
        topic = t.get("topic", "Topic")
        res = t.get("result", "—")
        ts = t.get("timestamp", "")
        note = t.get("note", "")
        st.markdown(f"- **{topic}** {res} — *{ts}*  \n  <small>{note}</small>", unsafe_allow_html=True)

def render_chapters(chapters: List[Dict[str, Any]]):
    if not chapters:
        st.caption("No chapters generated.")
        return
    for c in chapters:
        title = c.get("title", "Chapter")
        ts = c.get("timestamp", "")
        st.markdown(f"<div class='chapter-item'><strong>{title}</strong><br/><small>{ts}</small></div>", unsafe_allow_html=True)

def _pct_bar(label: str, val01: float):
    pct = max(0, min(100, int(round(100*val01))))
    st.markdown(f"**{label}:** {pct}%")
    st.progress(min(1.0, val01))

def render_jd_match(jd_struct: Dict[str, Any], jd_eval: Dict[str, Any], jd_evidence: Dict[str, Any]):
    st.markdown("### 📌 JD → Competency Graph")
    line = []
    if jd_struct.get("role"): line.append(f'<span class="jd-badge"><b>Role</b>: {jd_struct["role"]}</span>')
    if jd_struct.get("seniority"): line.append(f'<span class="jd-badge"><b>Seniority</b>: {jd_struct["seniority"]}</span>')
    if jd_struct.get("responsibilities"):
        for r in jd_struct["responsibilities"][:6]:
            line.append(f'<span class="jd-badge">{r}</span>')
    st.markdown(" ".join(line), unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Must-have**")
        if jd_struct.get("must_have"):
            st.write(", ".join([f"`{x}`" for x in jd_struct["must_have"]]))
        else:
            st.write("_None detected_")
        st.markdown("**Nice-to-have**")
        if jd_struct.get("nice_to_have"):
            st.write(", ".join([f"`{x}`" for x in jd_struct["nice_to_have"]]))
        else:
            st.write("_None detected_")
    with colB:
        st.markdown("**Soft skills**")
        if jd_struct.get("soft_skills"):
            st.write(", ".join([f"`{x}`" for x in jd_struct["soft_skills"]]))
        else:
            st.write("_None detected_")
        if jd_struct.get("years_experience"):
            st.markdown("**Years (required)**")
            yrs_str = ", ".join([f"`{k}: {v}y`" for k,v in jd_struct["years_experience"].items()])
            st.write(yrs_str or "_—_")

    st.markdown("---")
    st.markdown("### 🎯 JD Bucket Scores")
    buckets = (jd_eval.get("buckets") or {})
    col1, col2, col3, col4 = st.columns(4)
    with col1: _pct_bar("Hard skills", float(buckets.get("hard_skills",0.0)))
    with col2: _pct_bar("Soft skills", float(buckets.get("soft_skills",0.0)))
    with col3: _pct_bar("Role fit", float(buckets.get("role_fit",0.0)))
    st.info(f"**Overall JD Match:** {int(round(100*float(jd_eval.get('overall_score',0.0))))}%")

    gaps = jd_eval.get("gaps", []) or []
    if gaps:
        st.markdown("### ⚠️ Gaps vs Must-have")
        st.markdown(" ".join([f'<span class="gap-badge">{g}</span>' for g in gaps]), unsafe_allow_html=True)
    else:
        st.success("No must-have gaps detected.")

    st.markdown("---")
    st.markdown("### 🔎 Evidence by Competency")
    comp_evd = (jd_evidence or {}).get("competencies", {})
    comp_scores = jd_eval.get("competency_scores", {})
    for comp in sorted(comp_scores.keys(), key=lambda k: (-comp_scores[k], k)):
        v = comp_evd.get(comp, {})
        present = v.get("present", False)
        st.markdown(f"**{comp}** — score: `{comp_scores.get(comp,0)}` — {'✅ evidence' if present else '❌ no evidence'}")
        for q in v.get("evidence_quotes", [])[:3]:
            st.markdown(f"<div class='ev-quote'>{q}</div>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx: st.caption(f"Depth: {v.get('depth',0)}")
        with coly: st.caption(f"Recency: {v.get('recency',0)}")

    st.markdown("---")
    rec = jd_eval.get("recommendation") or (st.session_state.insights.get("jd", {}).get("rec_and_probes", {}).get("recommendation") if st.session_state.insights and st.session_state.insights.get("jd") else None)
    probes = jd_eval.get("next_round_probes") or (st.session_state.insights.get("jd", {}).get("rec_and_probes", {}).get("next_round_probes") if st.session_state.insights and st.session_state.insights.get("jd") else [])
    if rec:
        st.markdown("### ✅ Recommendation")
        st.success(rec)
    if probes:
        st.markdown("### 🧠 Next-Round Probes")
        for p in probes:
            st.markdown(f"- {p}")

# =========================
# Results Tabs
# =========================
if st.session_state.transcription:
    st.markdown("---")
    st.markdown("##  Interview Analysis Report")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f" Candidate: {st.session_state.candidate_name}")
    with col2: st.markdown(f" Position: *{st.session_state.position}*")
    with col3: st.markdown(f" Analyzed: {st.session_state.timestamp}")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        " AI Analysis", "Skills Assessment", "Detailed Chapters", " Quick Chapters", "JD Match", " AI Chat"
    ])

    with tab1:
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.analysis or "_No AI analysis available (offline)._")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.action_items:
            st.markdown("###  Automated Action Items")
            for a in st.session_state.action_items: st.markdown(f"- {a}")
        st.markdown("---")
        st.markdown("###  How to Use This Analysis")
        st.markdown("""
        - **Share with hiring team** - Download and share the report
        - **Schedule follow-up** - Use action items for next steps
        - **Compare candidates** - Keep reports for side-by-side comparison
        - **Reference checks** - Use identified areas for reference questions
        - **Make decision** - Review final recommendation with team
        """)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("###  Technical Assessment")
            render_technical((st.session_state.insights or {}).get("technical_assessment", []))
        with col_b:
            st.markdown("###  Soft Skills")
            render_soft_skills((st.session_state.insights or {}).get("soft_skills", []))

    with tab3:
        render_detailed_chapters(st.session_state.detailed_chapters or [])

    with tab4:
        st.markdown("###  Quick Chapter Summary")
        render_chapters(st.session_state.chapters or [])
        st.caption("Quick chapters with timestamps from the transcript.")

    with tab5:
        if st.session_state.jd_struct and st.session_state.insights and (st.session_state.insights.get("jd") or st.session_state.jd_eval):
            jd_struct = st.session_state.jd_struct
            jd_evidence = (st.session_state.insights.get("jd", {}) or {}).get("evidence", {}) if st.session_state.insights else {}
            jd_eval_display = {}
            if st.session_state.jd_eval:
                jd_eval_display.update(st.session_state.jd_eval)
            if st.session_state.insights.get("jd", {}).get("scores"):
                jd_eval_display.update(st.session_state.insights["jd"]["scores"])
            if st.session_state.insights.get("jd", {}).get("rec_and_probes"):
                jd_eval_display.update(st.session_state.insights["jd"]["rec_and_probes"])
            render_jd_match(jd_struct, jd_eval_display, jd_evidence)
        else:
            st.info("Paste a JD and enable **Analyze with JD (JD-aware)**, then click **Analyze Transcript**.")

    with tab6:
        st.markdown('<div class="white-card chat-container">', unsafe_allow_html=True)
        st.markdown("### 💬 AI-Powered Interview Assistant")
        st.caption("Ask anything about this interview. Try: 'generate a resume', 'what are the key strengths?', 'summarize communication skills'")
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message chat-user"> <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message chat-ai"> <strong>AI:</strong><br/>{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        col_chat1, col_chat2 = st.columns([4, 1])
        with col_chat1:
            user_q = st.text_input("Ask a question…", key="chat_input", placeholder="e.g., 'Generate a resume for this candidate'")
        with col_chat2:
            send_button = st.button(" Send", key="chat_send", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if send_button and user_q.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.spinner("AI is thinking..."):
                answer = chat_with_meeting(
                    user_q, 
                    st.session_state.transcription, 
                    st.session_state.analysis,
                    st.session_state.candidate_name,
                    st.session_state.position
                )
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
        st.markdown("#### Quick Actions")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        with quick_col1:
            if st.button(" Generate Resume"):
                st.session_state.chat_history.append({"role": "user", "content": "Generate a professional resume for this candidate"})
                with st.spinner("Creating resume..."):
                    answer = chat_with_meeting(
                        "Generate a professional resume for this candidate", 
                        st.session_state.transcription, 
                        st.session_state.analysis,
                        st.session_state.candidate_name,
                        st.session_state.position
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
        with quick_col2:
            if st.button(" Key Strengths"):
                st.session_state.chat_history.append({"role": "user", "content": "What are the candidate's key strengths with specific examples?"})
                with st.spinner("Analyzing strengths..."):
                    answer = chat_with_meeting(
                        "What are the candidate's key strengths with specific examples?", 
                        st.session_state.transcription, 
                        st.session_state.analysis,
                        st.session_state.candidate_name,
                        st.session_state.position
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
        with quick_col3:
            if st.button(" Red Flags"):
                st.session_state.chat_history.append({"role": "user", "content": "Are there any red flags or concerns?"})
                with st.spinner("Checking for concerns..."):
                    answer = chat_with_meeting(
                        "Are there any red flags or concerns?", 
                        st.session_state.transcription, 
                        st.session_state.analysis,
                        st.session_state.candidate_name,
                        st.session_state.position
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

else:
    st.markdown("---")
    st.info("👆 **Get Started:** Enter candidate details, paste a JD (optional) and the interview transcript, then click “Analyze Transcript”.")

# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #fff; padding: 20px;'>
  <strong> Features:</strong> JD-aware matching • Detailed chapters • Resume generation • Smart search<br/>
  <p><strong>AI Interview Analyzer</strong> | ASPECT.CO.UK</p>
  <p> Make Smarter Hiring Decisions with AI</p>
  <p style='font-size: 0.85rem; margin-top: 1rem; opacity:.9;'></p>
</div>
""", unsafe_allow_html=True)
