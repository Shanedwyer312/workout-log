# CLAUDE.md — workout-log

This repo (Shanedwyer312/workout-log) holds Shane's personal workout tracker, a rebuild of the old BodySpace app he misses.
The app is called **SetRep** (written with a capital R). It was previously called Iron Log.

## Name vs. app ID
- Visible app name: **SetRep**. This can be changed any time without affecting data.
- Android app ID: **`com.shanedwyer.workoutlog`**. This is permanent. Never change it: a different ID makes
  Android treat it as a new app, so updates won't install over the old one and data is lost.
- The repo name `workout-log` is neutral on purpose so the visible name can change later.

## What it does today
- Workout logging and saved routines
- Body stats
- Progress photos (with side-by-side compare)
- A weekly muscle map, colored by sets per muscle

## Where it's going
- Android only. The goal is a standalone app installed on his phone, ideally as a downloadable APK.
- Claude should be able to keep making updates easily, the same way the setlist app works:
  Claude edits this repo and pushes, and the phone picks up the new version.
- Shane works on a Windows PC and isn't an app developer. Prefer a setup where he doesn't have to install
  or run build tools himself (for example, GitHub Actions building the APK on each push). Explain choices plainly.

## Current stage: web app first
- The repo is public and served by GitHub Pages (main branch, root folder) at
  https://shanedwyer312.github.io/workout-log/ — every push updates it within a minute or two.
- Shane uses it on his phone via Chrome → "Add to Home screen".
- Files: `index.html` (the whole app), `sw.js` (offline copy; bump `CACHE` name when adding files to it),
  `manifest.webmanifest` (home-screen install), `icons/`, `fonts/` (bundled so it works offline).
- Data lives in the browser's IndexedDB database `setrep` (stores: meta, workouts, stats, photos, blobs).
  A small `Local` layer in `index.html` stands in for the old Claude storage API.
- Backup button (top right) exports one JSON file with everything, photos included, and imports it back
  (import replaces all data). This is how data moves from the web version into the Android app later.
- The repo is public: never commit personal data, backups or photos.
- Coach (in `index.html`): double progression per exercise. `exSet()` = rep range + weight jump (defaults 8–12,
  +5 lb upper / +10 lb lower), editable per exercise from the exercise history sheet. `coachFor()` = target,
  `setMark()` = PR / REP / ▲ = ▼ per set, `summarize()` = the "Workout done" screen.
- Sync: Backup screen → "Sync for weekly report". The upload key is stored only in IndexedDB meta `sync` (never in
  backups/exports). After workouts/stats/routine changes the app PUTs `data/setrep-data.json` (numbers only, no
  photos) to the PRIVATE repo Shanedwyer312/workout-data and reads `reports/latest.md` back to show on the Week tab.
  The weekly report itself is written by a scheduled Claude task following workout-data's CLAUDE.md.
- Exercise library: `LIB` in `index.html` (primary muscles = 1 set, secondary = 0.5 on the map and in reports).
  To promote one of Shane's custom exercises into `LIB`, add the entry plus its name(s) to `LIB_ALIASES`;
  `mergeCustomIntoLib()` moves his matching custom exercise (workouts, routines, settings) over on next app start
  and on import, so history stays attached and nothing double counts.
- Muscle map: the body shapes come from `tools/muscle-map/source.png`, a color-coded chart (one flat color per
  muscle group, made with ChatGPT). `tools/muscle-map/trace.py source.png out.js` traces it into the
  `BODY_VIEWS` block in `index.html` (front/back: outline, skin areas, muscle regions, detail lines).
  To change the body, make a new chart with the same colors and re-run the tracer. The dark "sculpted"
  look (shading, glow, heat colors) is all CSS/SVG styling in `index.html`, separate from the shapes.

## The plan (Android app, later)
- Capacitor app shell around the web app.
- GitHub Actions builds the APK on every push and publishes it on the repo's Releases page, where Shane installs it.
- One permanent signing key, so each update installs over the old version without losing data.
  The repo is public, so the key must live only in GitHub Actions secrets, never in the repo.
- All data stored on the phone (IndexedDB), photos included, with Export / Import backup buttons.
- Fully offline.

- When converting: the backup export currently downloads through the browser; inside the Android app it will
  need Capacitor's Filesystem/Share plugins instead. Shane moves his data over with Export → Import.

## History
`index.html` started as a Claude artifact that saved through Claude's artifact runtime. That was replaced with
on-device storage (IndexedDB) plus Export/Import, and it now works fully offline.

## Working with Shane
- Keep explanations plain.
- Push changes straight to this repo. Don't hand over files to copy and paste.
- Test changes in a real browser before pushing (pushes go live on his phone right away).
- Bump `APP_VERSION` in `index.html` on every push (shown at the bottom of the Backup screen) so Shane can
  confirm his phone has the latest version.
