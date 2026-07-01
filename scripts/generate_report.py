#!/usr/bin/env python3
"""
Daily Futures Trading Report Generator
Runs via GitHub Actions twice daily.
Searches the web via Tavily, then generates the HTML report via Anthropic API.
"""

import argparse
import os
import sys
from datetime import datetime

import anthropic
from tavily import TavilyClient

# ── Config ────────────────────────────────────────────────────────────────────
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000
OUTPUT_FILE = "index.html"

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert ICT (Inner Circle Trader) futures analyst. You write comprehensive trading reports in valid HTML format using ICT Smart Money methodology.

ICT TERMINOLOGY — USE EXACTLY:
- OB: Order Block — last opposing candle before a strong move
- FVG: Fair Value Gap — imbalance / price gap left by fast moves
- BSL: Buy-Side Liquidity — equal highs, stops above prior highs
- SSL: Sell-Side Liquidity — equal lows, stops below prior lows
- MSS: Market Structure Shift — first sign of trend reversal
- CISD: Change in State of Delivery — shift in how price is being delivered (bullish to bearish or vice versa)
- OTE: Optimal Trade Entry — 62–79% Fibonacci retracement zone
- PDH/PDL: Prior Day High / Prior Day Low
- SMT: Smart Money Technique — divergence between correlated pairs (ES vs NQ)
- AMD: Accumulation, Manipulation, Distribution — ICT Power of Three

CRITICAL: NEVER use "BOS" or "CHoCH". Always substitute MSS and CISD.

─── DESIGN ───────────────────────────────────────────────────────────────────
Dark trading terminal theme. All CSS inline in a <style> tag. No external CSS or JS libraries. Mobile responsive.

CSS variables to define in :root:
  --bg: #0d1117
  --surface: #161b22
  --surface2: #1c2128
  --border: #30363d
  --text: #e6edf3
  --text-muted: #8b949e
  --blue: #388bfd
  --green: #3fb950
  --red: #f85149
  --yellow: #d29922
  --purple: #bc8cff

Phase badge background colors:
  Accumulation → #0d2018 (green text)
  Manipulation → #2d1e00 (yellow text)
  Distribution → #2d0f0f (red text)
  Re-Accumulation → #0d1a2d (blue text)

─── REPORT STRUCTURE — 8 SECTIONS ──────────────────────────────────────────

SECTION 1 — 🚨 Alert Banner (always first, always prominent):
  Color-coded full-width banner:
  - NARRATIVE FLIP: bg #2d1e00, left border 4px solid var(--yellow)
  - NARRATIVE CONFIRMED / NARRATIVE HOLDS: bg #0d2018, left border 4px solid var(--green)
  - ALL QUIET / EOD QUIET: bg var(--surface), left border 4px solid var(--border)
  Content: what the market believed at last close vs. what actually changed overnight/today.
  Include explicit note if overnight holders need to re-evaluate positions.

SECTION 2 — 🎭 Manipulation Detection:
  A. Sentiment Table — AAII bullish %, AAII bearish %, Fear & Greed Index score + label,
     COT net positioning (crude, gold), Put/Call ratio. Plain-English interpretation per row.
  B. Narrative Trap Cards (1–3) — each card:
     - Title (purple, bold)
     - "The Narrative" — what media/consensus says
     - "Reality Check" — what price action or COT data actually shows
     - "ICT Read" — which AMD phase this reflects
     - "Exploitation Setup" — specific trade setup with entry zone, target, invalidation
  C. Smart Money Flow — bullet list by asset, what institutions appear to be doing

SECTION 3 — 🌍 Geopolitical Watchlist:
  Table: Event | Status (🔴 Active / 🟡 Watching / 🟢 Resolved) | Affected Assets | Bias Shift
  Include all active conflicts, OPEC decisions, central bank events, political risks

SECTION 4 — 🧠 ICT Market Phase Assessment:
  2-column card grid for: NQ, ES, CL (WTI), GC (Gold), SI (Silver), BTC
  Each card: asset ticker + name, last price, phase badge, 2–3 sentences with SPECIFIC price levels
  Use OB, FVG, BSL, SSL, MSS, CISD, OTE, PDH/PDL throughout. Never be vague.

SECTION 5 — 🏦 Sector Assessment:
  Table: Sector | Move Likelihood (High/Moderate/Low badge) | Bias (↑ ↓ →) | Reasoning (1 sentence)
  Sectors: Energy, Defense, Precious Metals, Healthcare, Technology, Financials, Industrials/Materials, Crypto

SECTION 6 — ✅ ICT Actionable Steps:
  Five time-block cards with dark background and colored time label.
  (See edition-specific instructions for which session blocks to use)

SECTION 7 — ⚠️ Risk & Mindset:
  Table with rows:
  - Position Sizing: max risk per trade given current volatility
  - Narrative Discipline: what thesis to avoid over-trusting
  - Upcoming Catalysts: next 24–48 hrs economic events
  - ICT Mindset: one sharp ICT principle for today
  - Overnight Hold Warning: explicit guidance on holding positions overnight

SECTION 8 — 📊 Market Snapshot:
  Table: Asset | Last Close | Change | Bias (↑ ↓ → with color) | Key Levels
  Assets: NQ, ES, WTI Crude, Brent Crude, Gold, Silver, BTC

Footer: small text — "Educational purposes only. Not financial advice."

─── TONE ───────────────────────────────────────────────────────────────────
Sharp ICT trader voice. Always skeptical of consensus. Always asking "who benefits if retail believes this?"
Specific price levels throughout — never vague placeholders.
Overnight events always reflected. Never carry stale narrative from a prior session.

─── OUTPUT FORMAT ──────────────────────────────────────────────────────────
Return ONLY the complete HTML document.
Start with exactly: <!DOCTYPE html>
End with exactly: </html>
No markdown. No code fences. No commentary before or after the HTML."""


# ── Web research ──────────────────────────────────────────────────────────────
def run_searches(edition: str, today_str: str) -> dict:
    """Run Tavily web searches and return raw results dict."""
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    base_queries = [
        f"ES NQ futures price levels key levels {today_str}",
        f"crude oil WTI gold silver futures price {today_str}",
        f"Bitcoin BTC price crypto market {today_str}",
        f"AAII investor sentiment survey bullish bearish latest",
        f"CNN fear greed index {today_str}",
        f"COT commitments of traders crude oil gold latest report",
        f"put call ratio options market {today_str}",
        f"geopolitical news overnight military conflict {today_str}",
        f"Middle East Iran oil Strait of Hormuz {today_str}",
        f"Russia Ukraine China Taiwan economic market impact {today_str}",
        f"financial media headlines futures market narrative {today_str}",
        f"bank analyst forecast S&P 500 oil gold consensus {today_str}",
    ]

    eod_extras = [
        f"S&P 500 Nasdaq stock market close results {today_str}",
        f"sector ETF performance today XLE XLK XLV XLF {today_str}",
        f"Fed FOMC economic data released {today_str}",
    ]

    overnight_extras = [
        f"S&P 500 Nasdaq futures overnight outlook premarket {today_str}",
        f"OPEC oil supply decision output {today_str}",
    ]

    queries = base_queries + (eod_extras if edition == "eod" else overnight_extras)

    results = {}
    for query in queries:
        try:
            resp = tavily.search(query, search_depth="basic", max_results=3)
            results[query] = resp.get("results", [])
            print(f"  ✓ {query[:70]}")
        except Exception as exc:
            print(f"  ✗ FAILED '{query[:60]}': {exc}", file=sys.stderr)
            results[query] = []

    return results


def format_context(results: dict) -> str:
    """Flatten search results into a readable context block for Claude."""
    lines = []
    for query, items in results.items():
        lines.append(f"\n### {query}")
        if not items:
            lines.append("(no results)")
            continue
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("content", item.get("snippet", ""))[:600]
            lines.append(f"**{title}**  \n{url}\n{snippet}\n")
    return "\n".join(lines)


# ── Report generation ─────────────────────────────────────────────────────────
def generate_html(edition: str, context: str, today_str: str) -> str:
    """Call Claude to generate the HTML report from search context."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if edition == "overnight":
        edition_block = f"""EDITION: OVERNIGHT EDITION (generated at midnight)

Header: sticky top bar — "📈 Daily Futures Trading Report" | date "{today_str}" | "Last updated: 12:00 AM ET"
Add a small badge next to the title: "OVERNIGHT EDITION" (bg #1a2a1a, color var(--green), font-size 11px, padding 3px 10px, border-radius 3px)

Section 1 label: 🚨 After-Hours / Overnight Alert

Section 6 — Actionable Steps blocks for TODAY's upcoming session:
  1. Pre-Market Prep (6–7 AM ET) — numbered steps
  2. London Kill Zone (2–5 AM ET) — what to observe
  3. NY Open Kill Zone (7–10 AM ET) — min 2 specific setups with levels; Silver Bullet window 9:50–10:10 AM
  4. NY Lunch (12–1:30 PM ET) — stand-down guidance
  5. NY Afternoon (1:30–4 PM ET) — continuation or reversal read

Section 8 column header: "Today's Bias"
"""
    else:
        edition_block = f"""EDITION: EOD EDITION (generated at 6 PM market close)

Header: sticky top bar — "📈 Daily Futures Trading Report" | date "{today_str}" | "Last updated: Close ET"
Add a small badge next to the title: "EOD EDITION" (bg #1a2a4a, color var(--blue), font-size 11px, padding 3px 10px, border-radius 3px)

Section 1 label: 🚨 EOD Alert
Banner label options: EOD ALERT — OVERNIGHT RISK | EOD CONFIRMED — NARRATIVE HOLDS | EOD QUIET
Content: what happened at today's close vs expectations. What to watch overnight. Overnight hold warnings.

Section 6 — Actionable Steps blocks for TOMORROW's upcoming session:
  1. Tonight — Overnight Watch (what to monitor before tomorrow's open)
  2. Pre-Market Prep — tomorrow 6–7 AM ET
  3. London Kill Zone — tomorrow 2–5 AM ET
  4. NY Open Kill Zone — tomorrow 7–10 AM ET — min 2 specific setups with levels
  5. NY Lunch / Afternoon — tomorrow 12–4 PM ET

Section 8 column header: "Tomorrow's Bias"
Overall report tone: debrief of today's session + game plan for tomorrow. "Here's what actually happened, here's what the media wants you to believe overnight, here's what you do tomorrow."
"""

    user_msg = f"""Today is {today_str}.

{edition_block}

─── WEB RESEARCH DATA ────────────────────────────────────────────────────────
{context}
──────────────────────────────────────────────────────────────────────────────

Generate the complete ICT futures trading report HTML.
Use MSS and CISD (never BOS or CHoCH).
Include specific price levels throughout — no vague placeholders.
Output ONLY valid HTML starting with <!DOCTYPE html>."""

    print(f"Calling Claude API (model: {MODEL}, max_tokens: {MAX_TOKENS})...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    html = response.content[0].text.strip()

    # Strip accidental markdown code fences
    if html.startswith("```"):
        lines = html.splitlines()
        html = "\n".join(lines[1:])
        if html.endswith("```"):
            html = html[: html.rfind("```")]

    if "<!DOCTYPE" not in html:
        raise ValueError(f"Response does not appear to be valid HTML. First 200 chars:\n{html[:200]}")

    # Trim anything before <!DOCTYPE
    start = html.index("<!DOCTYPE")
    html = html[start:]

    return html


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate ICT futures trading report")
    parser.add_argument("--edition", choices=["overnight", "eod"], required=True,
                        help="overnight = midnight report, eod = 6 PM report")
    args = parser.parse_args()

    today_str = datetime.now().strftime("%B %d, %Y")
    print(f"\n{'='*60}")
    print(f"Generating {args.edition.upper()} report — {today_str}")
    print(f"{'='*60}\n")

    # Step 1: Web research
    print("Step 1: Web research")
    search_results = run_searches(args.edition, today_str)
    context = format_context(search_results)
    print(f"  Collected {sum(len(v) for v in search_results.values())} results from {len(search_results)} queries\n")

    # Step 2: Generate HTML
    print("Step 2: Generating HTML report")
    html = generate_html(args.edition, context, today_str)
    print(f"  Generated {len(html):,} characters of HTML\n")

    # Step 3: Write file
    print(f"Step 3: Writing {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ Written to {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
