from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = APP_DIR / "NGS_TEAM_PAGE_2025_WEEKLY_V1_1.parquet"
DATA_PATH = Path(os.getenv("NGS_TEAM_PAGE_DATA", str(DEFAULT_DATA_PATH)))

st.set_page_config(
    page_title="Next Gen Stats — Team Snapshot",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEAM_NAMES = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAC": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs", "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams",
    "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
    "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
    "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans", "WAS": "Washington Commanders",
}

CORE_METRICS = [
    {"key": "off_epa_per_play", "label": "Offensive EPA / Play", "format": "epa",
     "description": "Expected points added per offensive play."},
    {"key": "def_epa_per_play_allowed", "label": "Defensive EPA / Play Allowed", "format": "epa",
     "description": "Expected points added allowed per defensive play."},
    {"key": "off_success_rate", "label": "Offensive Success Rate", "format": "percent",
     "description": "Share of offensive plays that generated positive EPA."},
    {"key": "def_success_rate_allowed", "label": "Defensive Success Rate Allowed", "format": "percent",
     "description": "Share of defensive plays that allowed positive EPA."},
    {"key": "motion_rate", "label": "Motion Rate", "format": "percent",
     "description": "Share of eligible offensive plays using motion."},
    {"key": "play_action_rate", "label": "Play-Action Rate", "format": "percent",
     "description": "Share of quarterback dropbacks using play action."},
    {"key": "blitz_rate", "label": "Blitz Rate", "format": "percent",
     "description": "Share of defensive quarterback dropbacks with a blitz."},
    {"key": "pressure_rate", "label": "Pressure Rate", "format": "percent",
     "description": "Share of defensive quarterback dropbacks generating pressure."},
]

IDENTITY_EXPLANATIONS = {
    "PLAY_ACTION_MOTION": "A manipulation-first passing profile built around play action and pre-snap motion.",
    "HIGH_VOLUME_SHORT_GAME": "A higher-volume passing profile that wins with shorter throws and quick distribution.",
    "VERTICAL_PASSING": "A downfield-oriented passing profile where verticality is a defining part of the offense.",
    "CONSTRAINT_HEAVY_PASSING": "A passing profile that leans on screens, RPOs and other quick constraints.",
    "UNDER_CENTER_ZONE": "Under-center structure with zone runs as the core of the ground game.",
    "SPREAD_GAP_MAN": "A spread-oriented run game built more around gap/man concepts than zone.",
    "PISTOL_HEAVY_ZONE": "Pistol and heavier personnel usage paired with a zone-heavy rushing foundation.",
    "UNDER_CENTER_GAP_MAN": "Under-center structure with gap/man concepts as the defining rushing scheme.",
    "FOUR_MAN_SPLIT_SAFETY": "A four-man-rush defense with split-safety structure and less dependence on extra pressure.",
    "LIGHT_BOX_MAN": "A lighter-box defensive profile with man coverage as a defining feature.",
    "PRESSURE_MAN": "Man coverage paired with an aggressive pressure profile.",
    "HEAVY_BOX_PRESSURE": "Heavier boxes and elevated pressure define the defensive structure.",
}

st.markdown(
    """
    <style>
        :root {
            --ink: #111827; --muted: #667085; --line: #e5e7eb;
            --panel: #ffffff; --canvas: #f7f8fa;
            --defined: #0f5132; --lean: #9a6700; --lean-soft: #fff7db;
        }
        .stApp { background: var(--canvas); }
        .block-container { max-width: 1320px; padding-top: 2rem; padding-bottom: 3rem; }
        [data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
        .page-kicker { font-size:.78rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#667085; margin-bottom:.35rem; }
        .team-title { font-size:clamp(2rem,4vw,3.4rem); font-weight:850; line-height:1; color:var(--ink); letter-spacing:-.045em; margin:0; }
        .team-subtitle { margin-top:.55rem; font-size:.98rem; color:var(--muted); }
        .section-title { margin-top:1.15rem; margin-bottom:.25rem; font-size:1.32rem; font-weight:800; color:var(--ink); letter-spacing:-.02em; }
        .section-copy { margin-top:0; margin-bottom:.9rem; color:var(--muted); font-size:.92rem; }
        .metric-card { min-height:190px; border:1px solid var(--line); border-radius:18px; padding:1.05rem; background:var(--panel); box-shadow:0 1px 2px rgba(16,24,40,.04); margin-bottom:.25rem; }
        .metric-label { font-size:.82rem; text-transform:uppercase; letter-spacing:.06em; font-weight:800; color:#667085; }
        .metric-value { margin-top:.35rem; font-size:2rem; line-height:1.05; font-weight:850; color:var(--ink); letter-spacing:-.04em; }
        .metric-meta { margin-top:.35rem; display:flex; align-items:center; gap:.45rem; flex-wrap:wrap; font-size:.82rem; color:#475467; }
        .pct-pill { display:inline-flex; align-items:center; padding:.22rem .48rem; border-radius:999px; font-weight:800; border:1px solid rgba(17,24,39,.08); }
        .metric-desc { margin-top:.68rem; font-size:.80rem; color:#667085; line-height:1.35; }
        .gradient-wrap { margin-top:.8rem; position:relative; height:9px; }
        .gradient-bar { height:7px; border-radius:999px; background:linear-gradient(90deg,#b42318 0%,#eab308 50%,#15803d 100%); opacity:.95; }
        .gradient-marker { position:absolute; top:-4px; width:3px; height:15px; border-radius:2px; background:#111827; box-shadow:0 0 0 2px rgba(255,255,255,.92); }
        .identity-row { display:grid; grid-template-columns:minmax(220px,320px) 1fr; gap:1rem; align-items:stretch; border:1px solid var(--line); border-radius:18px; background:#fff; padding:1rem; margin-bottom:.72rem; box-shadow:0 1px 2px rgba(16,24,40,.035); }
        .identity-left { display:flex; flex-direction:column; justify-content:center; gap:.5rem; }
        .identity-domain { font-size:.72rem; font-weight:850; letter-spacing:.1em; text-transform:uppercase; color:#667085; }
        .identity-badge { display:inline-flex; width:fit-content; align-items:center; border-radius:999px; padding:.46rem .72rem; font-size:.84rem; line-height:1; font-weight:850; }
        .identity-badge.defined { color:#fff; background:var(--defined); border:1px solid var(--defined); }
        .identity-badge.lean { color:var(--lean); background:var(--lean-soft); border:1.5px dashed #d4a72c; }
        .identity-name { font-size:1.02rem; font-weight:800; color:var(--ink); line-height:1.25; }
        .identity-explanation { display:flex; flex-direction:column; justify-content:center; color:#344054; line-height:1.5; font-size:.92rem; }
        .identity-confidence { margin-top:.35rem; font-size:.80rem; color:#667085; }
        .spotlight-card { border-radius:20px; background:linear-gradient(145deg,#111827 0%,#1f2937 100%); color:white; padding:1.25rem 1.3rem; box-shadow:0 10px 30px rgba(17,24,39,.12); }
        .spotlight-kicker { color:#cbd5e1; text-transform:uppercase; letter-spacing:.10em; font-weight:800; font-size:.73rem; }
        .spotlight-name { margin-top:.32rem; font-size:1.75rem; font-weight:850; letter-spacing:-.035em; line-height:1.05; }
        .spotlight-meta { margin-top:.25rem; color:#cbd5e1; font-size:.85rem; }
        .spotlight-metrics { margin-top:1rem; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem; }
        .spotlight-metric { padding:.72rem .75rem; border-radius:14px; background:rgba(255,255,255,.075); border:1px solid rgba(255,255,255,.10); }
        .spotlight-metric-label { font-size:.72rem; color:#cbd5e1; text-transform:uppercase; letter-spacing:.04em; font-weight:700; }
        .spotlight-metric-value { margin-top:.18rem; font-size:1.25rem; font-weight:850; color:white; }
        .spotlight-metric-pct { margin-top:.16rem; font-size:.76rem; color:#d1fae5; font-weight:700; }
        .season-context { margin-top:1rem; border-top:1px solid rgba(255,255,255,.14); padding-top:.9rem; color:#e5e7eb; font-size:.84rem; line-height:1.55; }
        @media (max-width:760px) { .identity-row { grid-template-columns:1fr; } .spotlight-metrics { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    required = {
        "season", "through_week", "team",
        "off_epa_per_play", "def_epa_per_play_allowed",
        "off_success_rate", "def_success_rate_allowed",
        "motion_rate", "play_action_rate", "blitz_rate", "pressure_rate",
        "show_team_identity_section", "show_ngs_spotlight_section",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("The team-page feed is missing required columns: " + ", ".join(missing))
    df = df.copy()
    df["season"] = pd.to_numeric(df["season"], errors="raise").astype(int)
    df["through_week"] = pd.to_numeric(df["through_week"], errors="raise").astype(int)
    df["team"] = df["team"].astype(str)
    return df

if not DATA_PATH.exists():
    st.error(
        "Team-page data file not found.\n\n"
        f"Expected: `{DATA_PATH}`\n\n"
        "Place `NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet` beside this app, "
        "or set the `NGS_TEAM_PAGE_DATA` environment variable to its path."
    )
    st.stop()

try:
    data = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Unable to load team-page feed: {exc}")
    st.stop()

def first_existing(columns: Iterable[str], frame: pd.DataFrame) -> str | None:
    for col in columns:
        if col in frame.columns:
            return col
    return None

def normalize_percentile(value) -> float | None:
    if pd.isna(value):
        return None
    value = float(value)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1:"st",2:"nd",3:"rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def format_value(value, fmt: str) -> str:
    if pd.isna(value):
        return "—"
    value = float(value)
    if fmt == "epa":
        return f"{value:+.3f}"
    if fmt == "percent":
        if abs(value) <= 1.5:
            value *= 100
        return f"{value:.1f}%"
    return f"{value:.2f}"

def format_spotlight_value(label: str | None, value) -> str:
    if label is None or pd.isna(value):
        return "—"
    value = float(value)
    low = label.lower()
    if "cpoe" in low:
        return f"{value:+.1f} pp"
    if "rush % over expected" in low:
        if abs(value) <= 1.5:
            value *= 100
        return f"{value:+.1f}%"
    if "share" in low:
        if abs(value) <= 1.5:
            value *= 100
        return f"{value:.1f}%"
    if "ryoe" in low:
        return f"{value:+.2f}"
    return f"{value:.2f}"

def metric_percentile_column(metric_key: str, frame: pd.DataFrame) -> str | None:
    return first_existing(
        [f"{metric_key}_percentile", f"{metric_key}_pctile", f"{metric_key}_percentile_rank"],
        frame,
    )

def metric_rank_column(metric_key: str, frame: pd.DataFrame) -> str | None:
    return first_existing([f"{metric_key}_rank", f"{metric_key}_nfl_rank"], frame)

def percentile_style(pct: float | None) -> tuple[str, str]:
    if pct is None:
        return "#667085", "#f2f4f7"
    hue = 120 * pct
    return f"hsl({hue:.0f} 62% 35%)", f"hsl({hue:.0f} 70% 94%)"

def render_metric_card(row: pd.Series, spec: dict, frame: pd.DataFrame) -> None:
    key = spec["key"]
    pct_col = metric_percentile_column(key, frame)
    rank_col = metric_rank_column(key, frame)
    pct = normalize_percentile(row.get(pct_col)) if pct_col else None
    rank = row.get(rank_col) if rank_col else None
    border, soft = percentile_style(pct)
    pct_label, marker = "Percentile unavailable", 50.0
    if pct is not None:
        pct_int = max(1, min(100, int(round(pct * 100))))
        pct_label = f"{ordinal(pct_int)} percentile"
        marker = pct * 100
    rank_html = ""
    if rank is not None and not pd.isna(rank):
        try:
            rank_html = f"<span>#{int(rank)} NFL</span>"
        except (TypeError, ValueError):
            pass
    st.markdown(
        f"""
        <div class="metric-card" style="border-top:4px solid {border};">
            <div class="metric-label">{html.escape(spec["label"])}</div>
            <div class="metric-value">{html.escape(format_value(row.get(key), spec["format"]))}</div>
            <div class="metric-meta">
                <span class="pct-pill" style="background:{soft}; color:{border};">{html.escape(pct_label)}</span>
                {rank_html}
            </div>
            <div class="gradient-wrap">
                <div class="gradient-bar"></div>
                <div class="gradient-marker" style="left:calc({marker:.2f}% - 1px);"></div>
            </div>
            <div class="metric-desc">{html.escape(spec["description"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def identity_code(row: pd.Series, domain: str) -> str | None:
    for col in [f"{domain}_archetype_code", f"{domain}_display_archetype", f"{domain}_archetype"]:
        value = row.get(col)
        if value is not None and not pd.isna(value):
            return str(value)
    return None

def identity_label(row: pd.Series, domain: str) -> str | None:
    for col in [f"{domain}_display_label", f"{domain}_identity_label", f"{domain}_display_archetype"]:
        value = row.get(col)
        if value is not None and not pd.isna(value):
            return str(value)
    return None

def identity_strength(row: pd.Series, domain: str) -> str | None:
    value = row.get(f"{domain}_display_strength")
    if value is not None and not pd.isna(value):
        return str(value).upper()
    qual = row.get(f"{domain}_qualification")
    if qual == "DEFINED_ARCHETYPE":
        return "DEFINED"
    if qual == "ARCHETYPE_LEAN":
        return "LEAN"
    return None

def render_identity(row: pd.Series, domain: str, domain_label: str) -> None:
    if not bool(row.get(f"{domain}_display_identity")):
        return
    code = identity_code(row, domain)
    label = identity_label(row, domain) or (code or "Identity")
    strength = identity_strength(row, domain) or "DEFINED"
    explanation = IDENTITY_EXPLANATIONS.get(
        code or "",
        "This profile most closely matches the displayed archetype based on the frozen identity model.",
    )
    is_lean = strength == "LEAN"
    badge_class = "lean" if is_lean else "defined"
    badge_text = "LEAN" if is_lean else "DEFINED IDENTITY"
    confidence_copy = (
        "Lean: the profile points toward this archetype, but the fit does not clear "
        "the stricter threshold required for a defined identity."
        if is_lean else
        "Defined: the profile clears the stricter fit and separation thresholds for a true team identity."
    )
    st.markdown(
        f"""
        <div class="identity-row">
            <div class="identity-left">
                <div class="identity-domain">{html.escape(domain_label)}</div>
                <div class="identity-badge {badge_class}">{html.escape(badge_text)}</div>
                <div class="identity-name">{html.escape(label)}</div>
            </div>
            <div class="identity-explanation">
                <div>{html.escape(explanation)}</div>
                <div class="identity-confidence">{html.escape(confidence_copy)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_spotlight_metric(label, value, pct) -> str:
    if label is None or pd.isna(label):
        return ""
    pct_norm = normalize_percentile(pct)
    pct_text = (
        f"{ordinal(max(1, min(100, int(round(pct_norm * 100)))))} percentile"
        if pct_norm is not None else "Percentile unavailable"
    )
    return f"""
        <div class="spotlight-metric">
            <div class="spotlight-metric-label">{html.escape(str(label))}</div>
            <div class="spotlight-metric-value">{html.escape(format_spotlight_value(str(label), value))}</div>
            <div class="spotlight-metric-pct">{html.escape(pct_text)}</div>
        </div>
    """

def render_spotlight(row: pd.Series) -> None:
    if not bool(row.get("show_ngs_spotlight_section")):
        return
    name = row.get("player_display_name")
    role = row.get("spotlight_type")
    position = row.get("player_position")
    opportunity_label = row.get("opportunity_label")
    opportunity = row.get("weekly_opportunity")
    meta_parts = [str(x) for x in [position, role] if x is not None and not pd.isna(x)]
    if opportunity_label is not None and not pd.isna(opportunity_label) and opportunity is not None and not pd.isna(opportunity):
        meta_parts.append(f"{opportunity_label}: {int(round(float(opportunity)))}")
    weekly_metrics = "".join(
        render_spotlight_metric(
            row.get(f"weekly_metric_{i}_label"),
            row.get(f"weekly_metric_{i}_value"),
            row.get(f"weekly_metric_{i}_percentile"),
        )
        for i in (1, 2, 3)
    )
    season_html = ""
    if bool(row.get("season_context_available")):
        items = []
        for i in (1, 2, 3):
            label = row.get(f"season_metric_{i}_label")
            value = row.get(f"season_metric_{i}_value")
            pct = normalize_percentile(row.get(f"season_metric_{i}_percentile"))
            if label is None or pd.isna(label) or pct is None:
                continue
            pct_int = max(1, min(100, int(round(pct * 100))))
            items.append(
                f"{html.escape(str(label))}: <strong>{html.escape(format_spotlight_value(str(label), value))}</strong> "
                f"({ordinal(pct_int)} percentile)"
            )
        if items:
            season_html = (
                '<div class="season-context"><strong>Season-to-date context:</strong> '
                + " &nbsp;•&nbsp; ".join(items) + "</div>"
            )
    st.markdown(
        f"""
        <div class="spotlight-card">
            <div class="spotlight-kicker">NGS Spotlight</div>
            <div class="spotlight-name">{html.escape(str(name))}</div>
            <div class="spotlight-meta">{html.escape(" · ".join(meta_parts))}</div>
            <div class="spotlight-metrics">{weekly_metrics}</div>
            {season_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("### Team Snapshot")
st.sidebar.caption("Historical replay demo")

seasons = sorted(data["season"].dropna().unique().tolist())
selected_season = st.sidebar.selectbox("Season", seasons, index=len(seasons) - 1)
season_data = data.loc[data["season"].eq(selected_season)].copy()

weeks = sorted(season_data["through_week"].dropna().unique().tolist())
selected_week = st.sidebar.selectbox("Through Week", weeks, index=len(weeks) - 1)
week_data = season_data.loc[season_data["through_week"].eq(selected_week)].copy()

teams = sorted(week_data["team"].dropna().unique().tolist(), key=lambda x: TEAM_NAMES.get(x, x))
selected_team = st.sidebar.selectbox(
    "Team",
    teams,
    format_func=lambda x: f"{TEAM_NAMES.get(x, x)} ({x})",
)

row = week_data.loc[week_data["team"].eq(selected_team)].iloc[0]

st.sidebar.divider()
st.sidebar.caption(
    "Historical replay: every value, identity and Spotlight uses only information available through the selected week."
)

team_name = TEAM_NAMES.get(selected_team, selected_team)
games_played = row.get("games_played")
games_text = ""
if games_played is not None and not pd.isna(games_played):
    games_text = f" · {int(games_played)} games played"

st.markdown(
    f"""
    <div class="page-kicker">Next Gen Stats · Team Snapshot</div>
    <div class="team-title">{html.escape(team_name)}</div>
    <div class="team-subtitle">{int(selected_season)} season · Through Week {int(selected_week)}{html.escape(games_text)}</div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div style="height:.65rem;"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Team Performance</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Eight fixed measures. Percentiles are performance-oriented: '
    '<strong>green is better, red is worse.</strong></div>',
    unsafe_allow_html=True,
)

for start in (0, 4):
    cols = st.columns(4)
    for col, spec in zip(cols, CORE_METRICS[start:start + 4]):
        with col:
            render_metric_card(row, spec, data)

if bool(row.get("show_team_identity_section")):
    st.markdown('<div class="section-title">Team Identity</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Only identities that clear the frozen display threshold are shown. '
        'A <strong>Defined Identity</strong> is a stronger classification; a <strong>Lean</strong> is directional '
        'and intentionally presented with less certainty.</div>',
        unsafe_allow_html=True,
    )
    render_identity(row, "pass", "Passing")
    render_identity(row, "rush", "Rushing")
    render_identity(row, "def", "Defense")

if bool(row.get("show_ngs_spotlight_section")):
    st.markdown('<div class="section-title">NGS Spotlight</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">A qualifying offensive-player tracking performance from the selected week.</div>',
        unsafe_allow_html=True,
    )
    render_spotlight(row)

st.markdown('<div style="height:.45rem;"></div>', unsafe_allow_html=True)

with st.expander("Methodology & demo limitations"):
    st.markdown(
        '''
**Historical replay**

The page is point-in-time. Selecting “Through Week N” uses only data available through that week.

**Team Identity**

Passing, rushing and defensive identities are independent. A domain is hidden when it does not clear the frozen qualification thresholds. A **Defined Identity** clears the stricter fit/separation standard. A **Lean** is a directional match that clears the lower display threshold but not the stricter Defined threshold.

**NGS Spotlight**

Spotlight is conditional; there is no quota. The public demo uses the free offensive-player Next Gen Stats feed (passing, receiving and rushing). Defensive-player tracking Spotlights are therefore unavailable in this demo. That is a data-access limitation rather than a product-design limitation. An internal NGS implementation can extend the same framework to defensive players.

**Renderer-only app**

This Streamlit file does not recalculate identities, percentiles or Spotlight eligibility. It renders the frozen `NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet` feed.
        '''
    )
