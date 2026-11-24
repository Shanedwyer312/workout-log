# CLAUDE.md — workout-log

This repo (Shanedwyer312/workout-log) holds Shane's personal workout tracker, a rebuild of the old BodySpace app he misses.
The app is called **SetRep** (written with a capital R). It was previously called Iron Log; the current
`index.html` still shows the old name and should be updated to SetRep when building starts.

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

## The plan
- Capacitor app shell around the web app.
- GitHub Actions builds the APK on every push and publishes it on the repo's Releases page, where Shane installs it.
- One permanent signing key, so each update installs over the old version without losing data.
- All data stored on the phone (IndexedDB), photos included, with Export / Import backup buttons.
- Fully offline.

## The one big change needed
`index.html` was built as a Claude artifact. It saves everything through Claude's artifact runtime
(`window.claude.use("db")`, `"user"` and `"assets"`: collections `workouts`, `stats`, `photos`, a profile doc,
and photo uploads). That runtime doesn't exist outside claude.ai, so as-is the page shows
"This tracker saves to your Claude account."
- Replace it with on-device storage (e.g. IndexedDB), with photos stored on the device too.
- Add Export / Import backup buttons so his history can never get stranded.
- The app must work fully offline.
- There is no existing workout history to migrate. The old artifact's saved data was empty.

## Working with Shane
- Keep explanations plain.
- Push changes straight to this repo. Don't hand over files to copy and paste.
- Don't start building until Shane says go.
