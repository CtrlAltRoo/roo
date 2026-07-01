# Daily Futures Trading Report — Project Memory

## What This Project Does

Twice daily, Claude scheduled tasks research futures markets and write a fresh `index.html` to this folder. A macOS LaunchAgent commits and pushes to GitHub 15 minutes after each write.

The result is a live webpage that updates itself twice daily with an ICT Smart Money-style trading report — once at midnight (overnight/pre-market report) and once at 6 PM (end-of-day assessment + tomorrow's game plan).

---

## Daily Automation Flow

```
12:00 AM  →  Claude scheduled task: daily-futures-report
               - Searches web for overnight news, geopolitical events, sentiment
               - Writes fresh index.html (OVERNIGHT EDITION) to this folder

12:15 AM  →  macOS LaunchAgent fires push-report.sh
               - git add -A
               - git commit -m "report: daily futures update YYYY-MM-DD"
               - git push origin main
               - Result logged to push.log

 6:00 PM  →  Claude scheduled task: daily-futures-eod (weekdays only)
               - Searches web for today's closing prices, sector performance
               - Overwrites index.html (EOD EDITION) with debrief + tomorrow's game plan

 6:15 PM  →  macOS LaunchAgent fires push-report.sh (same script, second fire)
               - git add -A
               - git commit -m "report: daily futures update YYYY-MM-DD"
               - git push origin main
               - Result logged to push.log
```

---

## File Structure

| File | Purpose |
|------|---------|
| `index.html` | The trading report — overwritten nightly by Claude |
| `push-report.sh` | Shell script that commits and pushes to GitHub |
| `com.roo.trading-report-push.plist` | macOS LaunchAgent definition (runs push-report.sh at 12:15 AM) |
| `push.log` | Auto-generated log of each push attempt |
| `CLAUDE.md` | This file — project memory |

---

## GitHub Repository

- **Remote:** https://github.com/CtrlAltRoo/roo.git
- **Branch:** `main`
- **Auth:** GitHub PAT embedded in remote URL (see git config)
- **User:** Roo / datsdatdat@gmail.com

To check the configured remote:
```bash
cd ~/Claude/Projects/trading-info-page && git remote -v
```

---

## Scheduled Tasks

### Overnight Report
- **Task ID:** `daily-futures-report`
- **Schedule:** Every day at 12:00 AM (midnight local time)
- **Location:** `~/Claude/Scheduled/daily-futures-report/SKILL.md`
- **What it does:** Researches overnight news, writes `index.html` (OVERNIGHT EDITION)
- **Does NOT:** Run git commands (LaunchAgent handles that)

### EOD Assessment
- **Task ID:** `daily-futures-eod`
- **Schedule:** Weekdays (Mon–Fri) at 6:00 PM local time
- **Location:** `~/Claude/Scheduled/daily-futures-eod/SKILL.md`
- **What it does:** Researches today's close, overwrites `index.html` (EOD EDITION) with debrief + tomorrow's game plan
- **Does NOT:** Run git commands (LaunchAgent handles that)

To view or edit tasks: open the Scheduled section in the Cowork sidebar.

---

## LaunchAgent

- **Plist label:** `com.roo.trading-report-push`
- **Installed at:** `~/Library/LaunchAgents/com.roo.trading-report-push.plist`
- **Fires:** 12:15 AM (after overnight report) and 6:15 PM (after EOD report) every day

### Install / Reinstall
```bash
chmod +x ~/Claude/Projects/trading-info-page/push-report.sh
cp ~/Claude/Projects/trading-info-page/com.roo.trading-report-push.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.roo.trading-report-push.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.roo.trading-report-push.plist
```

### Check it's loaded
```bash
launchctl list | grep trading
```

### Unload / disable
```bash
launchctl unload ~/Library/LaunchAgents/com.roo.trading-report-push.plist
```

### Trigger a manual push right now
```bash
bash ~/Claude/Projects/trading-info-page/push-report.sh
```

---

## Report Structure (8 Sections)

The HTML report Claude generates nightly follows this structure:

1. **🚨 Overnight Alert** — Narrative flip / confirmed / all quiet. Scans for events that occurred after market close (overnight, weekends) that may change the prevailing trade narrative. Always present.

2. **🎭 Manipulation Detection** — Three sub-sections:
   - Sentiment readings (AAII, Fear & Greed, COT, put/call ratio)
   - Active narrative traps (1–3 per day) — what media says vs. what institutions are doing, with specific exploitation setups
   - What smart money appears to be doing

3. **🌍 Geopolitical Watchlist** — All active global situations with status, affected assets, and bias shift

4. **🧠 ICT Market Phase Assessment** — NQ, ES, CL, GC, SI, BTC assessed against ICT Power of Three (Accumulation / Manipulation / Distribution / Re-Accumulation) with specific levels

5. **🏦 Sector Assessment** — Move likelihood and directional bias for Energy, Defense, Precious Metals, Healthcare, Technology, Financials, Industrials, Crypto

6. **✅ Actionable Steps** — Time-blocked ICT action plan: Pre-Market Prep, London Kill Zone, NY Open Kill Zone (Silver Bullet 9:50–10:10 AM), NY Lunch stand-down, NY Afternoon

7. **⚠️ Risk & Mindset** — Position sizing, narrative discipline, upcoming catalysts, ICT mindset reminder, overnight hold warnings

8. **📊 Market Snapshot** — Quick-reference table: NQ, ES, WTI, Brent, Gold, Silver, BTC with last close, move, bias, key levels

---

## Design

Dark trading terminal theme. No external dependencies — all CSS inline.

Key CSS variables:
- `--bg: #0d1117` (page background)
- `--surface: #161b22` (cards, tables)
- `--green: #3fb950` / `--red: #f85149` / `--yellow: #d29922` / `--purple: #bc8cff`

ICT phase badge colors: Accumulation=green, Manipulation=yellow, Distribution=red, Re-Accumulation=blue

---

## ICT Terminology Reference

| Term | Meaning |
|------|---------|
| OB | Order Block — last opposing candle before a strong move |
| FVG | Fair Value Gap — imbalance / price gap left by fast moves |
| BSL | Buy-Side Liquidity — equal highs, stops above prior highs |
| SSL | Sell-Side Liquidity — equal lows, stops below prior lows |
| MSS | Market Structure Shift — first sign of trend reversal |
| CISD | Change in State of Delivery — shift in how price is being delivered (bullish to bearish or vice versa) |
| OTE | Optimal Trade Entry — 62–79% Fibonacci retracement zone |
| PDH/PDL | Prior Day High / Prior Day Low |
| SMT | Smart Money Technique — divergence between correlated pairs (ES vs NQ) |
| AMD | Accumulation, Manipulation, Distribution — ICT Power of Three |

---

## Troubleshooting

**Push failed / check push.log:**
```bash
cat ~/Claude/Projects/trading-info-page/push.log
```

**Re-initialize git from scratch (if .git gets corrupted):**
```bash
cd ~/Claude/Projects/trading-info-page
rm -rf .git
git init -b main
git config user.email "datsdatdat@gmail.com"
git config user.name "Roo"
git remote add origin https://TOKEN@github.com/CtrlAltRoo/test-site.git
git add -A
git commit -m "rebuild: reinitialize repo"
git push -u origin main
```
Replace TOKEN with a fresh GitHub PAT (Settings → Developer settings → Personal access tokens → classic → repo scope).

**Scheduled task not writing the file:**
- Open Cowork → Scheduled → select the task → Run now
- Approve WebSearch and Write tool permissions when prompted
- Those approvals are saved for all future runs
- Do this for BOTH `daily-futures-report` and `daily-futures-eod`

**LaunchAgent not firing:**
- Make sure Cowork is open at midnight (scheduled tasks require the app to be running)
- Check `launchctl list | grep trading` to confirm it's loaded
- Run `bash ~/Claude/Projects/trading-info-page/push-report.sh` manually to test the push step independently
