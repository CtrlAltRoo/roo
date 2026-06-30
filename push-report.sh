#!/bin/bash
# Auto-push daily futures report to GitHub
# Runs nightly via LaunchAgent after Claude writes the HTML at midnight

REPO_DIR="$HOME/Claude/Projects/trading-info-page"
LOG="$REPO_DIR/push.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

cd "$REPO_DIR" || { echo "[$DATE] ERROR: could not cd to $REPO_DIR" >> "$LOG"; exit 1; }

git add -A

if git diff --cached --quiet; then
  echo "[$DATE] No changes to commit." >> "$LOG"
  exit 0
fi

git commit -m "report: daily futures update $(date '+%Y-%m-%d')"
git push origin main >> "$LOG" 2>&1

if [ $? -eq 0 ]; then
  echo "[$DATE] Push succeeded." >> "$LOG"
else
  echo "[$DATE] Push FAILED — check token or network." >> "$LOG"
fi
