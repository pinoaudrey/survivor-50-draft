# Survivor 50 — Fantasy Draft

A fantasy draft and scoring app for Survivor 50, hosted on GitHub Pages.

## Pages

| Page | Description |
|------|-------------|
| `survivor-draft.html` | Main app — leagues, drafts, standings |
| `tracker-entry.html` | Log episode events and save the week's CSV |
| `scoring.html` | Scoring reference guide |

---

## Local development

The app fetches `data/leagues.json` and `data/week_N.csv` on load, so you need a local server running to use it. The included `server.py` also handles auto-saving — leagues and week CSVs are written to disk automatically when you make changes.

### Start the server

```bash
python3 server.py
```

Then open **http://localhost:8765** in your browser.

> Stop the server with `Ctrl+C`.

### Weekly episode workflow

1. Watch the episode, open **http://localhost:8765/tracker-entry.html**
2. Check off events for each player
3. Hit **"💾 Save week_N.csv to data/"** — the file is written automatically
4. Commit and push to GitHub:

```bash
git add data/
git commit -m "Add week N scores"
git push
```

GitHub Pages will update within ~30 seconds and everyone will see the new standings on refresh.

---

## Data files

| File | Description |
|------|-------------|
| `data/leagues.json` | All leagues and draft picks — auto-saved by the app |
| `data/week_N.csv` | Episode scores — saved via tracker-entry, one file per episode |
