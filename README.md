# Next Gen Stats Team Snapshot — Streamlit Demo

This package contains the renderer for the historical Next Gen Stats team-page demo.

The app is intentionally a **renderer only**. It reads the frozen team-week feed and does not recalculate any model, percentile, identity, or Spotlight rule.

## Files

Keep these together:

```text
ngs_team_page_demo.py
requirements.txt
README.md
NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet
```

The expected frozen data file is `NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet`. You can override that location with the `NGS_TEAM_PAGE_DATA` environment variable.

## What the demo shows

**Team Performance** always renders eight fixed measures: offensive EPA/play, defensive EPA/play allowed, offensive success rate, defensive success rate allowed, motion rate, play-action rate, blitz rate, and pressure rate. Each card shows its NFL percentile on a **red → yellow → green** performance gradient, where green is better.

**Team Identity** is conditional. Passing, rushing and defensive identities are independent. A **Defined Identity** is shown with a solid badge and means the team cleared the stricter fit/separation standard. A **Lean** is shown with an amber dashed badge and means the team resembles that archetype but did not clear the stricter Defined threshold. The app does not force a single overall team archetype and never renders a “No Identity” badge.

**NGS Spotlight** is conditional. It displays a qualifying weekly QB, receiver, or rusher performance and adds point-in-time season context when the cumulative sample is large enough.

## Historical replay

The sidebar selectors are `Season`, `Through Week`, and `Team`. The 2025 V1 feed contains 32 teams × 18 weeks = 576 team-week rows. Selecting **Through Week N** uses only data available through that week.

## Demo limitation: offensive-player Spotlights only

The public/free Next Gen Stats feed used for the historical demo exposes offensive-player tracking data for passing, receiving, and rushing. It does not expose the internal defensive-player tracking data needed for equivalent defensive-player Spotlights.

For that reason, **V1 Spotlights are limited to offensive players**. This is a data-access limitation, not a product-design limitation. The same framework can support defensive players when connected to the internal NGS data source.

## Run locally

Recommended: Python 3.11 or newer.

### Windows PowerShell

```powershell
cd "C:\Users\shaan\WR ATD Model\ngs_team_page_demo"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run ngs_team_page_demo.py
```

### Windows Command Prompt

```bat
cd "C:\Users\shaan\WR ATD Model\ngs_team_page_demo"
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run ngs_team_page_demo.py
```

Streamlit will usually serve the app at `http://localhost:8501`.

## Optional custom data path

PowerShell:

```powershell
$env:NGS_TEAM_PAGE_DATA="C:\path\to\NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet"
streamlit run ngs_team_page_demo.py
```

Command Prompt:

```bat
set NGS_TEAM_PAGE_DATA=C:\path\to\NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet
streamlit run ngs_team_page_demo.py
```

## Architecture

```text
Upstream analytics
    ↓
Frozen weekly products
    ↓
NGS_TEAM_PAGE_2025_WEEKLY_V1.parquet
    ↓
Streamlit renderer
```

The Streamlit app should not refit clusters, recalculate identity qualification, recalculate league percentiles, select Spotlight candidates, or modify the frozen historical feed.
