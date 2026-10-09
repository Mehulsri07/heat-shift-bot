# OpusCube Team Brief (app name TBD)

Oct 8, 2026 · @Mehul Srivastava

We are building an Android app that tells a construction-site supervisor which hours are safe for outdoor work in extreme heat, and turns that plan into a Hindi voice note for the crew. The supervisor downloads the app from our link, sets up their site once, and shares the voice note to the crew's WhatsApp group in one tap. The same app also runs as a web link, as a fallback for anyone who cannot install it.

It is team OpusCube's entry for the WeMakeDevs x AWS environmental hackathon (Heat and Water track), due 11 October 2026. This doc is the single source of truth for humans and for every Claude Code session on the team.

### Open decisions

- **App name.** Needed for the icon label. The scaffold uses the placeholder `OpusCube` until the team decides.
- **Stop window against the `DANGER` action text.** The stop window counts `DANGER` hours, but the `DANGER` action says "light tasks only". Recommended fix: change the `DANGER` action to "Stop outdoor work; light tasks in shade only". Needs a human decision before A writes the plan template.
- **Exact deadline.** Confirm the cut-off time and time zone on the hackathon page.
- **Names.** Who takes role A, and who owns the video (see Unassigned work).
- **Replay date.** D picks the May 2025 Jaipur heat day for the demo.

## Workload division

Four people, four lanes, no shared files, and nobody waits on anybody. Every lane builds against a contract written in this brief and uses labelled fixtures until the real thing lands. A, B and C each drive a Claude Code session; Mehul holds both B and C, working the app and API first and the infra and release second. D owns the datasets and the lighter coding. The video, the interviews and the Hindi review have no owner yet (see Unassigned work).

| Role | Person | One-line job | Files owned |
|---|---|---|---|
| A: Risk and agent | to be named | Turn hourly weather into a safe, checked plan | `src/risk.py`, `src/agent.py`, `src/guard.py`, `src/handlers/planner.py`, `src/copy/hi.json`, `src/copy/en.json`, `tests/test_risk.py`, `tests/test_guard.py` |
| B: App screens | Mehul | Build every screen of the React app | Everything under `web/` except `web/android/` and `web/capacitor.config.json` |
| C: Infra, API and release | Mehul | Run AWS, the API, the Android build and every deploy | `template.yaml`, `samconfig.toml`, `src/handlers/api.py`, `src/voice.py`, `tests/test_api.py`, `web/android/`, `web/capacitor.config.json`, `README.md`, `PLAN.md`, `CLAUDE.md`, requirements files, `pytest.ini` |
| D: Data | Nemat | Supply the weather and cooling data, and the small modules that read it | `src/forecast.py`, `src/cooling.py`, `tests/test_forecast.py`, `tests/test_cooling.py`, `data/cooling_points_jaipur.json`, `scripts/seed_cooling_points.py`, `src/copy/red_flag.json` |

### A: Risk and agent

- `risk.py`: heat index, bands, direct-sun bump and stop window, with the full test list from the Heat risk engine section.
- `agent.py`: the Strands agent, its system prompt and three tools. The forecast and cooling tools are thin wrappers around D's functions.
- `guard.py`: the number check and the template fallback plan, with tests.
- `planner.py`: plan mode, voice mode (calls C's `make_voice_note`) and the daily run; saves the `Plans` row with a status.
- `src/copy/hi.json` and `en.json`: the band action lines and the template sentences. The native-speaker review of the Hindi is unassigned.
- Starts on labelled fixture hours, so nothing waits for D's forecast client.

### B: App screens

- Setup screen, plan screen and voice note player in `web/src/`.
- Hour-by-hour colour strip, stop-work window, red-flag box, Hindi and English toggle.
- Polling for the plan through `web/src/api.ts`, with loading, failed and retry states.
- Location and share through the Capacitor plugins. They also work in a browser, so B needs no Android Studio.
- Every UI string in `web/src/copy/hi.json` and `en.json`.
- Starts on labelled fixtures in `web/src/fixtures/`, so nothing waits for the live API.

### C: Infra, API and release

- AWS profile, budget alert, Bedrock access, and a Bedrock-only IAM user so A can run the agent locally.
- SAM template and every backend deploy; posts the live link in the team chat.
- `api.py` and `voice.py` (both already in the repo, with tests for the API).
- Android release: builds the APK from B's code, installs it on a real phone, checks the location prompt and the share sheet, and hosts the download.
- README, architecture slide, and keeping this brief current.
- Chases Builder Center verification for all four members, and tests the app from a phone outside the team.

### D: Data

Datasets and lightweight coding only.

- `forecast.py`: the Open-Meteo client, forecast and past dates, with a test. Do this first: the replay date and A's integration both need it.
- The replay date: pick the May 2025 Jaipur heat day, using the forecast client to look at the real numbers.
- `data/cooling_points_jaipur.json`: 10 hand-verified cooling points in Jaipur.
- `cooling.py`: nearest cooling points from DynamoDB by straight-line distance, with a test.
- `scripts/seed_cooling_points.py` (already written; D owns it now), which loads that file.
- `src/copy/red_flag.json`: the red-flag message in Hindi and English, typed in by hand and checked by a native speaker. No Claude session may write or reword it.
- Data check: compare the numbers the app shows for the replay date against the raw Open-Meteo response.

### Unassigned work (needs an owner)

Nobody owns these yet. The video is a hard requirement of the submission, so it needs a name first.

- **The demo video** (required): script, real-world footage, voiceover, edit, upload and the submission itself. A, B and C supply the screen recordings.
- **Native-speaker review of the Hindi text** from A (`src/copy/hi.json`) and B (`web/src/copy/hi.json`).
- **Interviews** with 3 to 5 real supervisors or workers (optional). Without them, the video and README must not quote or paraphrase any user.

### Contracts between lanes

Each row is the only thing two lanes need to agree on. The consumer codes against the contract now and swaps in the real thing when it lands.

| Provider | Consumer | Contract | Until it lands, the consumer uses |
|---|---|---|---|
| C: `api.py` | B | The API contract section, mirrored in `web/src/api.ts` | Labelled fixtures in `web/src/fixtures/` |
| D: `forecast.get_hourly(lat: float, lon: float, date: str) -> list[dict]` | A | 24 items, one per hour of that local date in `Asia/Kolkata`: `{"hour": "HH:MM", "temp_c": float, "rh": float}`. A past date returns historical weather. Raises `ForecastError` on any failure | A labelled fixture list |
| D: `cooling.nearest(lat: float, lon: float, limit: int = 3) -> list[dict]` | A | Nearest first: `{"name", "type", "lat", "lon", "distance_km"}`. An empty list when there are no points | An empty list |
| C: `voice.make_voice_note(text: str, language: str) -> str` | A | Returns the S3 key of the MP3 | Already in the repo |
| A: the `Plans` row | C | The data model section | Fixture rows in `tests/test_api.py` |
| D: `src/copy/red_flag.json` | C | `{"hi": "...", "en": "..."}` | `api` answers a dangerous plan with an error until the file exists |
| B: the web build | C | `npm run build` passes on `main` | The scaffold already in `web/` |

**Fallback for the critical path:** `forecast.py` is the one piece of D's code the core flow cannot run without. If it is not on `main` by Friday 10:00 IST, A writes it and D moves to `cooling.py`.

## Timeline

Feature freeze is **Saturday 10 October, 12:00 IST**. After that we only fix bugs, record and submit.

Work runs in three phases. Until Friday 10:00 everyone builds alone against contracts and fixtures. From Friday 10:00 the lanes join up in one fixed order: D's forecast into A's planner, A's planner into C's deploy, C's live link into B's app. Saturday is fixes, recording and the video.

| When | A | B | C | D | Video (owner needed) |
|---|---|---|---|---|---|
| Thu 8 Oct, night | `risk.py` and its tests passing | Setup and plan screens on fixtures | AWS profile, Bedrock access, first deploy; debug APK built from the scaffold | `forecast.py` and its test, against real Open-Meteo responses | Owner named |
| Fri 9 Oct, to 10:00 | Agent returns a plan from fixture hours; `guard.py` and its tests | Screens call `api.ts` with polling; colour strip | Live link posted; Bedrock-only access handed to A | Replay date chosen; `red_flag.json` typed in and checked | Script v1 |
| Fri 9 Oct, 10:00 to evening | `planner` on the real forecast, saving to `Plans`; replay mode | Switch from fixtures to the live API; voice player and share | Redeploy with A's planner; APK from B's code on a real phone | 10 cooling points in the data file; `cooling.py` and its test | Real-world footage |
| Fri 9 Oct, night | Voice mode; cooling tool wired in | Hindi and English toggle; error states | APK download hosted; cooling points seeded; 06:00 schedule; clean logs | Data check of the replay numbers | Storyboard |
| Sat 10 Oct, to 12:00 | Bug fixes only | Fixes from the Hindi review | README and architecture slide; final APK | Bug fixes in own modules | Hindi review done |
| Sat 10 Oct, afternoon | Screen-record the plan flows | Screen-record the app | Freeze; install and test from a fresh phone | Standby | Voiceover and edit |
| Sun 11 Oct | Standby | Standby | Repo public, links checked | Standby | Final cut, upload, submit early |

**Friday-evening milestone:** on a real phone, location in and plan out, against the deployed backend.

If the Friday-evening milestone slips, cut in this order: cooling points, then the 06:00 schedule, then the voice note, then the APK (ship the web link alone). Never cut setup, the daily plan or the red-flag message.

## Checklists

For tracking. Tick your own boxes as you finish them; the Timeline above says when each is due.

**A: Risk and agent**

- [ ] `risk.py` and its tests passing (Thu night)
- [ ] Agent returns a plan from fixture hours (Fri 10:00)
- [ ] `guard.py` and its tests, including the template fallback (Fri 10:00)
- [ ] Band action lines and template sentences in `src/copy/hi.json` and `en.json` (Fri 10:00)
- [ ] `planner` runs on the real forecast and saves to `Plans` (Fri evening)
- [ ] Replay mode works for a past date (Fri evening)
- [ ] Voice mode, and the cooling tool wired in (Fri night)
- [ ] Screen recording of the plan flows (Sat afternoon)

**B: App screens**

- [x] Setup screen on fixtures (Thu night)
- [x] Plan screen on fixtures, with the colour strip and red-flag box (Thu night)
- [x] Screens call `api.ts`, with polling, loading, failed and retry states (Fri 10:00)
- [ ] Switched from fixtures to the live API (Fri evening)
- [ ] Voice note player and share (Fri evening)
- [x] Hindi and English toggle; every string in the copy files (Fri night)
- [ ] Fixes from the Hindi review (Sat 12:00)
- [ ] Screen recording of the app (Sat afternoon)

**C: Infra, API and release**

- [x] Repo, brief and SAM template (template passes `sam validate --lint`)
- [x] `api.py` with its tests passing, and `voice.py`
- [x] App scaffold in `web/`, and a debug APK built from it
- [ ] AWS profile, budget alert and Bedrock access (Thu night)
- [ ] First deploy done and the live link posted (Fri 10:00)
- [ ] Bedrock-only access handed to A (Fri 10:00)
- [ ] Redeployed with A's planner (Fri evening)
- [ ] APK built from B's code and run on a real phone: location prompt and share sheet checked (Fri evening)
- [ ] APK download hosted; cooling points seeded; 06:00 schedule checked; logs clean (Fri night)
- [ ] README finalised and architecture slide made (Sat 12:00)
- [ ] App installed and tested from a phone outside the team (Sat afternoon)
- [ ] All four members verified on Builder Center
- [ ] Repo public, links checked (Sun)

**D: Data**

- [ ] `forecast.py` and its test, against real Open-Meteo responses (Thu night)
- [ ] Replay date chosen: a real May 2025 Jaipur heat day (Fri 10:00)
- [ ] `src/copy/red_flag.json` typed in by hand and checked by a native speaker (Fri 10:00)
- [ ] 10 hand-verified cooling points in `data/cooling_points_jaipur.json` (Fri evening)
- [ ] `cooling.py` and its test (Fri evening)
- [ ] Data check: the app's replay numbers match the raw Open-Meteo response (Fri night)

**Unassigned (needs an owner)**

The video is a hard requirement of the submission.

- [ ] Video owner named (Thu night)
- [ ] Video script v1 (Fri 10:00)
- [ ] Real-world footage filmed (Fri evening)
- [ ] Hindi text from A and B reviewed by a native speaker (Sat 12:00)
- [ ] Voiceover and edit (Sat afternoon)
- [ ] Final cut uploaded and submitted, at least 3 hours before the deadline (Sun)
- [ ] Optional: 3 to 5 interviews with supervisors or workers. Without them, quote no users

## The hackathon

We compete in the Heat and Water track of the WeMakeDevs x AWS environmental hackathon. Each track is judged separately, so we only compete against other Heat and Water entries.

### Hard requirements

- Every member must verify a student profile on AWS Builder Center. Do this today.
- The project must use at least one AWS open-source tool or be deployed on AWS. We do both: Strands Agents and SAM CLI (open source), deployed on Lambda.
- Submission includes a recorded demo video of at most 3 minutes. There is no live demo; the video is all the judges see.
- Deadline: 11 October 2026. Confirm the exact cut-off time on the hackathon page.

### Judging criteria and how we meet each one

| Criterion | What judges ask | Our answer |
|---|---|---|
| Idea and Impact | Does it fix a real environmental problem, and what changes for the people living with it? | Outdoor workers face life-threatening heat; one supervisor's decision protects a whole crew |
| Built on AWS | AWS open source or AWS services | Strands Agents, SAM, Lambda, API Gateway, Bedrock, Polly, DynamoDB, S3, CloudFront, EventBridge |
| Design and usability | Can someone outside the team use it, built for where they are? | An Android app with one setup form, no login, Hindi voice notes; workers need no app and no reading |
| Execution | Does it work? One working feature beats five half-done ones | One flow works end to end: location in, hourly plan and voice note out |
| Demo video | 3 minutes: what it does, who it's for, where AWS fits | The app on a real phone, replaying a real May 2025 Jaipur heat day with real numbers |

AWS costs: we deploy into Mehul's existing AWS account under a separate `opuscube` profile, with a budget alert at $10. Organisers give $25 in credits on request. The build should cost a small fraction of that.

## The problem and our user

Outdoor workers in Rajasthan keep working through dangerous afternoon heat because nobody turns the weather forecast into a shift decision. Heat forecasts exist; site-level instructions don't.

**Primary user: the site supervisor or contractor.** One supervisor sets shift timing for 20 to 50 workers. A single worker can't stop at noon, but a supervisor can move the shift. Every screen is designed for this person, on an Android phone, outdoors.

**Secondary user: the workers.** Many prefer voice over text and use basic Android phones. They never install our app. They receive the plan as a short Hindi voice note that the supervisor shares to the crew's WhatsApp group.

## What the product does

The app has two screens, setup and plan, and four flows listed in build priority. Flows 1 and 2 are the minimum shippable product.

### Getting the app

1. The supervisor opens our link in a phone browser. The page is the app itself, with a "Download the Android app" button.
2. They download the APK, allow the install, and open it. Android shows an unknown-source warning because we are not on the Play Store.
3. Anyone who cannot install keeps using the same link in the browser. Both run the same code.

### Flow 1: Supervisor setup (once per site)

1. Picks a language: Hindi or English.
2. Taps "Use my location" and grants permission. A manual latitude and longitude entry sits underneath, for the demo and for when permission is refused.
3. Types a site name (for example, "Tonk Road site").
4. Sets shift hours (default 07:00 to 18:00) and answers one yes/no question: is the work mostly in direct sun?
5. Saves. The app stores the returned `site_id` on the phone and goes straight to the plan screen. There is no login.

### Flow 2: Daily plan (core feature)

1. The plan screen has two tabs, Today and Tomorrow, and opens on Tomorrow.
2. The app asks the API for the plan and polls every 2 seconds until it is ready. After 60 seconds it shows a retry button.
3. Behind the API, the system fetches the hourly forecast, and the risk engine scores every shift hour into a band.
4. The agent writes a short plan from those scores: safe hours, mandatory breaks, the stop-work window, water reminders and one reason line ("heat index 46°C at 14:00").
5. The screen shows an hour-by-hour colour strip, the stop-work window, the plan text, nearby cooling points and a "Make crew voice note" button.
6. At 06:00 IST every day a scheduled job rebuilds today's plan for every site, so it is ready when the supervisor opens the app.

Every hour in the strip shows its band name and temperature as text as well as colour, so it reads in bright sun and for colour-blind users.

### Flow 3: Crew voice note

1. "Make crew voice note" converts the plan into a Hindi voice note of 20 to 30 seconds using Amazon Polly. The voice note is always in Hindi, whatever the app language.
2. The app plays it and offers Share, which opens the Android share sheet with the audio file. The supervisor picks the crew's WhatsApp group. We do not integrate WhatsApp directly.

### Flow 4: Red-flag safety message (fixed text)

Whenever any hour is rated Danger or worse, the plan screen shows a fixed, human-reviewed message: confusion, stopped sweating, fainting or very hot skin are signs of heat stroke; move the person to shade, cool them with water and call 108 immediately. This text lives in `src/copy/red_flag.json`, a file only humans edit, is attached by the API when the plan is read, and is shown word for word. It is never generated by the model and never reworded in the app.

### Demo-only: replay mode

A date field on the plan screen requests a plan for a past date. The system uses historical weather for that date instead of the forecast. The video uses a real May 2025 heat day in Jaipur, because October weather will not show the problem.

## Heat risk engine

The risk engine is plain, deterministic Python in `src/risk.py`. The AI model never decides a band, a temperature or a time; it only explains what the engine returns. The app never computes them either. This is our main safety argument to the judges.

**Inputs per hour:** air temperature (°C) and relative humidity (%) from Open-Meteo, plus the site's `direct_sun` flag.

**Step 1: Heat index.** Use the US National Weather Service Rothfusz regression with its published adjustments (NOAA WPC). The formula works in °F, so convert in and out. Heat index assumes shade; direct sun can add up to about 8°C.

```python
def heat_index_c(temp_c: float, rh: float) -> float:
    """NWS heat index (Rothfusz + adjustments). Input/output in Celsius."""
    t = temp_c * 9 / 5 + 32
    hi = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if hi >= 80:
        hi = (-42.379 + 2.04901523*t + 10.14333127*rh - 0.22475541*t*rh
              - 0.00683783*t*t - 0.05481717*rh*rh + 0.00122874*t*t*rh
              + 0.00085282*t*rh*rh - 0.00000199*t*t*rh*rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * ((17 - abs(t - 95)) / 17) ** 0.5
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return (hi - 32) * 5 / 9
```

**Step 2: Band.** Rate the hour on both columns below and take the higher band. Both are needed: Rajasthan's pre-monsoon heat is very dry, and in dry air the heat index can read below the air temperature.

| Band | Heat index (°C) | Air temperature (°C) | Action shown to supervisor |
|---|---|---|---|
| `SAFE` | below 27 | below 40 | Normal work, regular water |
| `CAUTION` | 27 to below 32 | 40 to below 42 | Normal work, water every 15 to 20 minutes |
| `EXTREME_CAUTION` | 32 to below 39 | 42 to below 45 | Shade break every hour; move heaviest tasks to the morning |
| `DANGER` | 39 to below 52 | 45 to below 47 | Light tasks only, long shade breaks, buddy checks |
| `EXTREME_DANGER` | 52 and above | 47 and above | Stop outdoor work |

Heat-index bands follow the NWS four-tier scale. The 40, 45 and 47°C air-temperature cut-offs follow IMD's heatwave criteria for the plains. The 42°C cut-off and the action text are our product decisions; we say so in the video. The `DANGER` action text is under review (see Open decisions).

**Step 3: Adjustments and outputs.**

- If `direct_sun` is true, raise every hour by one band (capped at `EXTREME_DANGER`).
- `stop_window` is the longest continuous run of `DANGER` or worse hours inside the shift, as `{"start": "HH:MM", "end": "HH:MM"}`, or null. `end` is the end of the last hour in the run, so hours 12, 13, 14 and 15 give 12:00 to 16:00.
- Return, per hour: `hour` (`HH:MM`), `temp_c`, `rh`, `heat_index_c` (1 decimal), `band`. Also return `stop_window` and `max_band`.

**Tests** (`tests/test_risk.py`) must cover: heat index against at least five values read from the NWS heat index chart; every band boundary; the dry-air case where air temperature decides the band; the direct-sun bump; and stop-window detection.

## Architecture and tech stack

One React codebase ships twice, as an Android APK and as a web link, and both talk to one serverless Python backend. Everything runs in one AWS region (`us-east-1` unless the team agrees otherwise) and deploys from a single SAM template.

```
Android app and web link (one React codebase)
        |
Amazon CloudFront (one HTTPS domain)
        |-- app files --> Amazon S3 (web build and APK download)
        |-- /api/* ----> API Gateway + api Lambda --> Amazon DynamoDB
                                |  async
                                v
EventBridge Scheduler --> planner Lambda (Strands agent + risk engine) --> DynamoDB
     (06:00 IST)                |
                                |--> Open-Meteo (hourly forecast)
                                |--> Amazon Bedrock (Claude Haiku)
                                |--> Amazon Polly (Hindi voice, MP3)
                                |--> Amazon S3 (voice note files)
```

The app only ever talks to CloudFront. `planner` is the only part that calls the model, the weather service and Polly.

### Request flow

1. The Android app carries its screens inside the APK. The web link loads the same screens from S3 through CloudFront.
2. The app calls `/api/...` on our CloudFront domain. CloudFront forwards those calls to API Gateway, which triggers the `api` Lambda.
3. `api` validates the input, reads or writes DynamoDB, saves a `pending` plan row, asynchronously invokes `planner`, and returns at once.
4. `planner` runs the Strands agent. The agent calls the forecast tool and the risk tool, and the cooling-point tool if needed.
5. The agent writes the plan text from tool output only. The output guard checks every number. `planner` saves the plan as `ready`, or `failed` if anything broke.
6. The app polls the plan route until the status changes.
7. For a voice note, `api` invokes `planner` in voice mode. `planner` sends the saved Hindi script to Polly, stores the MP3 in S3, and the API hands the app a time-limited link.
8. EventBridge Scheduler triggers `planner` at 06:00 IST for every registered site.

### Stack

| Layer | Choice | Notes |
|---|---|---|
| App UI | React, Vite and TypeScript, in `web/` | No router, UI kit, state library or CSS framework; two screens and plain CSS |
| Android packaging | Capacitor | Wraps the built web app into an APK; plugins for location, share and file download only |
| Hosting | Amazon S3 (private) behind Amazon CloudFront | Serves the web build, the APK download and forwards `/api/*`; gives one HTTPS domain |
| HTTP entry | Amazon API Gateway (HTTP API), routes under `/api` | Throttled; allows cross-origin calls from the Android app's origin |
| Compute | AWS Lambda: `api` and `planner` | `planner` is invoked async so no request waits on the model |
| Agent framework | Strands Agents SDK (AWS open source, Python) | Tools are Python functions with the `@tool` decorator; version pinned |
| Model | Claude Haiku on Amazon Bedrock | Exact ID set through the `BEDROCK_MODEL_ID` env var; don't rely on Strands' default |
| Weather | Open-Meteo forecast API and archive API | Free, no key; hourly `temperature_2m` and `relative_humidity_2m`; archive for replay mode |
| Risk engine | `src/risk.py`, pure Python | No AWS or network calls; fully unit-tested |
| Voice | Amazon Polly, voice `Kajal`, neural engine, MP3 output | Use language code `hi-IN` so numbers are read in Hindi |
| Database | Amazon DynamoDB, on-demand | Three tables (see Data model) |
| File storage | Amazon S3 | One bucket for the web build and APK, one for generated voice notes |
| Scheduler | Amazon EventBridge Scheduler | Daily 06:00 IST (`Asia/Kolkata` time zone) |
| Logs | Amazon CloudWatch Logs | Lambda default |
| Infrastructure as code | AWS SAM CLI (open source) | `sam build && sam deploy`; the build runs in Docker |
| Local testing | pytest, `sam local`, `npm run dev` | Vite proxies `/api` to the deployed backend |

### Known gotchas

- **The Android app is a different origin.** Its screens load from `https://localhost` inside the app, so its API calls are cross-origin. The API allows that origin; B reads the API base URL from a Vite env var, never a hard-coded string.
- **Location needs permission and HTTPS.** In the APK, use the Capacitor location plugin so Android shows its permission prompt. In a browser, location works only on HTTPS or `localhost`.
- **Not on the Play Store.** The APK installs with an unknown-source warning. The signing keystore never goes in the repo.
- **API Gateway cuts requests at 30 seconds.** That is why plans are built in the background and polled.
- **The API is public and triggers paid Bedrock calls.** It is throttled, and a plan that already exists is reused, not rebuilt.
- **Bedrock access.** Anthropic models may need a one-time use-case form in the console, and newer models are called through an inference-profile ID.
- **Polly output.** Always request MP3; it plays in the Android app and in every browser.
- **Open-Meteo time zone.** It returns UTC unless you pass `timezone=Asia/Kolkata`; always pass it.
- **CloudFront is slow to change.** Creating it takes several minutes, and a new web build needs a cache invalidation.
- **Lambda package size.** Measured on 8 October: Strands and its dependencies are 69 MB unzipped, well inside the 250 MB limit, so both functions stay as zips.

## API contract and data model

Five routes, three tables, two Lambdas, three agent tools. This section is the shared interface between A, B and C: don't change it without agreeing in the team chat first.

### API routes (owner: C, consumer: B)

All requests and responses are JSON. Errors return `{"error": "<code>"}` with a 4xx or 5xx status; the app turns the code into a sentence from its own copy files.

| Route | Request body | Success | Errors |
|---|---|---|---|
| `POST /api/sites` | `name`, `lat`, `lon`, `language`, `shift_start`, `shift_end`, `direct_sun` | 201 `{"site_id"}` | 400 `invalid_<field>` |
| `GET /api/sites/{site_id}` | none | 200, the site | 404 `site_not_found` |
| `POST /api/sites/{site_id}/plans` | `date` | 202 `{"status": "pending"}`, or 200 `{"status": "ready"}` if that plan already exists | 400 `invalid_date`, 404 `site_not_found` |
| `GET /api/sites/{site_id}/plans/{date}` | none | 200, the plan (below) | 404 `plan_not_found` |
| `POST /api/sites/{site_id}/plans/{date}/voice` | none | 202 `{"audio_status": "pending"}`, or 200 `{"audio_status": "ready"}` if it already exists | 404 `plan_not_found`, 409 `plan_not_ready` |

Creating a site does not start a plan; the app requests it. Any route can also return 400 `invalid_json`, 404 `not_found`, 429 `rate_limited` or 500 `server_error`.

**Validation in `api`:** `name` 1 to 60 characters; `lat` −90 to 90; `lon` −180 to 180; `language` is `hi` or `en`; hours are `HH:MM` with `shift_start` before `shift_end`; `direct_sun` is a boolean; `site_id` is a UUID; `date` is `YYYY-MM-DD` and no more than 3 days ahead. A past date means replay mode.

**Stuck plans:** a plan or voice note still `pending` after 150 seconds is treated as dead. The next request for it starts `planner` again.

### The plan response

| Field | Type | Notes |
|---|---|---|
| `status` | `pending`, `ready` or `failed` | When not `ready`, only `status`, `site_id` and `date` are present |
| `site_id`, `date` | string | |
| `source` | `forecast` or `replay` | |
| `hours` | list | Each item: `hour`, `temp_c`, `rh`, `heat_index_c`, `band`, straight from the risk engine |
| `stop_window` | `{"start", "end"}` or null | |
| `max_band` | band name | |
| `plan_text` | string | In the site's language; passed the output guard |
| `red_flag` | string or null | The fixed text, present when `max_band` is `DANGER` or worse |
| `cooling_points` | list | Each item: `name`, `type`, `lat`, `lon`, `distance_km`; may be empty |
| `audio_status` | `none`, `pending`, `ready` or `failed` | |
| `audio_url` | string or null | Link to the MP3, valid for one hour, present when `audio_status` is `ready` |

### DynamoDB tables

| Table | Keys | Attributes |
|---|---|---|
| `Sites` | PK `site_id` (string, UUID) | `name`, `lat`, `lon`, `language` (`hi` or `en`), `shift_start` (`HH:MM`), `shift_end`, `direct_sun` (bool), `created_at` |
| `Plans` | PK `site_id`, SK `date` (`YYYY-MM-DD`) | `status`, `hours`, `stop_window`, `max_band`, `plan_text`, `voice_text`, `cooling_points`, `audio_status`, `audio_s3_key`, `source`, `updated_at` |
| `CoolingPoints` | PK `city`, SK `point_id` | `name`, `lat`, `lon`, `type` (`water`, `shade` or `clinic`), `verified_by` |

`updated_at` is an ISO timestamp in `Asia/Kolkata`. `planner` must refresh it on every write, because `api` uses it to spot stuck plans.

### Lambda functions

| Function | Trigger | Responsibility |
|---|---|---|
| `api` (C) | API Gateway, routes under `/api` | Validate input; read and write `Sites`; write the `pending` plan row; async-invoke `planner`; attach the red-flag text; sign the audio link; always answer in JSON |
| `planner` (A) | Async invoke `{site_id, date, mode}`, where `mode` is `plan` or `voice`; EventBridge `{all_sites: true}` | `plan`: build the plan and voice script, run the guard, save to `Plans`. `voice`: call `make_voice_note`, save the audio key. On any error, set the status to `failed` |

### Agent tools (in `src/agent.py`, Strands `@tool`)

| Tool | Signature | Returns |
|---|---|---|
| `get_hourly_forecast` | `(lat: float, lon: float, date: str) -> list[dict]` | Hourly `temp_c` and `rh` for that local date; a thin wrapper around D's `forecast.get_hourly` |
| `score_hours` | `(hours: list[dict], direct_sun: bool, shift_start: str, shift_end: str) -> dict` | Output of `risk.py`: per-hour bands, `stop_window`, `max_band` |
| `nearest_cooling_points` | `(lat: float, lon: float, limit: int = 3) -> list[dict]` | Closest points from `CoolingPoints`; a thin wrapper around D's `cooling.nearest` |

`make_voice_note(text: str, language: str) -> str` is not an agent tool. It is a plain function in `src/voice.py` (C) that `planner` calls in voice mode: Polly MP3 written to S3, returns the S3 key. The model does not decide whether a voice note gets made.

**Agent system prompt must enforce:**

1. Always call `score_hours` before writing a plan.
2. Never state a temperature, time or band that does not appear in tool output.
3. Return two texts: the supervisor plan, at most 120 words, in the site's language; and the voice script, at most 60 words, always in Hindi.
4. Hindi must be simple and conversational, not formal.
5. Do not write the red-flag message; the API attaches the fixed text whenever `max_band` is `DANGER` or worse.

**Output guard:** after the agent responds, `planner` checks that every number in the plan text and in the voice script appears in the `score_hours` output. If either check fails, `planner` uses the template-built text instead of the agent's.

## Repo structure, ownership and setup

One repo, one owner per file, so the three Claude Code sessions never edit the same file. Owner letters match the Workload division.

```
repo-root/
  PLAN.md                       # this brief (C)
  CLAUDE.md                     # one line that loads PLAN.md into Claude Code sessions (C)
  README.md                     # problem, architecture, AWS services, setup (C)
  template.yaml                 # SAM: CloudFront, buckets, API, 2 Lambdas, 3 tables, schedule, IAM (C)
  samconfig.toml                # deploy settings (C)
  requirements.txt              # dev install: runtime pins plus pytest (C)
  pytest.ini                    # puts src/ on the import path (C)
  ruff.toml                     # Python lint and security rules (C)
  .github/workflows/ci.yml      # the checks every pull request must pass (C)
  src/
    requirements.txt            # runtime pins, packaged by SAM (C)
    risk.py                     # heat index + bands, no I/O (A)
    forecast.py                 # Open-Meteo forecast + archive client (D)
    cooling.py                  # nearest cooling points (D)
    agent.py                    # Strands agent, tools, system prompt (A)
    guard.py                    # output number check + template fallback (A)
    voice.py                    # Polly -> S3 (C)
    handlers/
      api.py                    # routes, validation, hand-off to planner (C)
      planner.py                # build and save the plan; voice mode; daily run (A)
    copy/
      hi.json                   # band actions and template sentences, Hindi (A)
      en.json                   # band actions and template sentences, English (A)
      red_flag.json             # the fixed red-flag message, both languages; humans only (D)
  web/                          # the app (B, except the two C entries marked below)
    package.json
    vite.config.ts
    capacitor.config.json       # app ID and name (C)
    .env.example                # API base URL and dev proxy target
    index.html
    src/
      main.tsx, App.tsx
      api.ts                    # API client and polling
      screens/                  # Setup and Plan
      copy/hi.json, en.json     # every UI string
      fixtures/                 # labelled fixture responses for building before the API is live
    android/                    # Capacitor's Android project (C; committed, build outputs ignored)
  data/
    cooling_points_jaipur.json  # hand-verified points (D)
  scripts/
    seed_cooling_points.py      # load data/ into DynamoDB (D)
  tests/
    test_risk.py                # (A)
    test_guard.py               # (A)
    test_forecast.py            # (D)
    test_cooling.py             # (D)
    test_api.py                 # (C)
    test_copy.py                # Hindi and English copy stay in step (C)
```

### Repo conventions

- **Backend code root is `src/`.** Both Lambdas are built from it, so imports are flat: `import risk`, `import voice`. Not `from src import risk`.
- **Handlers** are `handlers.api.handler` and `handlers.planner.handler`, each `def handler(event: dict, context: object) -> dict`. `planner.py` exists as a placeholder so the stack deploys; A replaces the body.
- **Tests** run from the repo root with `pytest`; they also use flat imports.
- **Backend copy** ships inside the package: load it with `Path(__file__).parent / "copy" / "hi.json"` from a module in `src/`. The red-flag text is separate, in `src/copy/red_flag.json` as `{"hi": "...", "en": "..."}`; `api` returns an error for a dangerous plan if it is missing.
- **`planner` is never retried** on failure, so a crash cannot build or voice the same plan twice. Set the status to `failed` and log.
- **CI checks every pull request, and `main` only accepts pull requests that pass it** (`.github/workflows/ci.yml`): Python lint with security rules, tests, dependency audits, the app's lint, type-check and build, the SAM template and Lambda package, a secret scan and code scanning. Run the same commands locally first (rule 13). A lint finding is fixed in the code, not silenced; an ignore needs a one-line reason beside it.
- **The one shared edit.** The Checklists section of this file is for tracking: every lane ticks its own boxes there, in the same pull request as the work that finishes them. Tick only your own, and change nothing else in `PLAN.md`.
- **The APK is a build output.** It is never committed; C builds it from `main` and uploads it.
- **The app is scaffolded.** `web/` already builds: `npm run build` type-checks and builds the web app, and `npm run android` builds it and syncs it into `web/android`. B replaces the placeholder screen in `App.tsx`; only C runs the Android build.
- **`web/src/api.ts` is the API contract in TypeScript**: the types and one function per route. If the contract changes, change this brief first, then that file.
- **App ID and name.** The Android app ID is `com.opuscube.app` and must not change once people have installed the app. The display name `OpusCube` is a placeholder, set in `web/capacitor.config.json` and `web/android/app/src/main/res/values/strings.xml`.
- **Capacitor's config is JSON on purpose.** Its CLI cannot load a `.ts` config with TypeScript 7 on Node 22.
- **App environment.** Copy `web/.env.example` to `web/.env.local` and fill it in; `.env.local` is never committed. Set `VITE_FIXTURES=1` there to run the app on the labelled fixtures in `web/src/fixtures/` without a backend; a production build must leave it unset.
- **App design.** The look is recorded in `DESIGN.md` (colours, type, components and the rules for using them), `PRODUCT.md` (product facts) and `.impeccable/surfaces/` (the chosen direction, "Shade Card"): each hour is a flat chip of colour with its band name and temperature printed beside it. Keep new screens inside that system: square corners, flat colour, the five band colours used only for bands.

### Setup, in order

1. Everyone: create and verify an AWS Builder Center student profile.
2. Everyone: pull the repo. Claude Code sessions load this brief automatically, through `CLAUDE.md`.
3. C: set up the `opuscube` AWS profile and a Budgets alert at $10.
4. C: get Bedrock access for Claude Haiku in `us-east-1`, and create a Bedrock-only IAM user for A.
5. A, C and D: install Python 3.11+, then `pip install -r requirements.txt`. C also needs AWS CLI v2, SAM CLI and Docker.
6. B: install Node.js (current LTS), then `npm install` inside `web/`. Only C needs Android Studio.
7. C: `sam build && sam deploy`, then post the CloudFront link in the team chat.
8. C: build the web app, sync it to the web bucket and invalidate CloudFront.
9. C: build the APK against the live API and upload it to the download path.
10. D: fill `data/cooling_points_jaipur.json`; C runs `scripts/seed_cooling_points.py` against the deployed table.

### Environment variables

Backend, set in `template.yaml`: `BEDROCK_MODEL_ID`, `SITES_TABLE`, `PLANS_TABLE`, `COOLING_TABLE`, `AUDIO_BUCKET`, `PLANNER_FUNCTION_NAME`, `POLLY_VOICE_ID=Kajal`, `TZ_NAME=Asia/Kolkata`.

App, set at build time: `VITE_API_BASE`. Empty for the web build, which shares the API's domain; the CloudFront URL for the APK build.

## Rules for Claude Code sessions

If you are a Claude Code session reading this file, these rules override your defaults. Humans: read them too, because your session follows them.

### Scope

1. Ask the human which role (A, B, C or D) you are working for. Edit only files that role owns in the repo tree above. If a change is needed elsewhere, write it up for the owner instead of making it.
2. Build only what is in this brief. If something seems missing, ask before adding a feature, a file, an AWS service or a dependency.
3. Prefer the smallest working version. One flow that runs end to end beats several that almost do.

### Safety-critical rules

4. Never let model output decide a band, temperature, time or threshold. Those come only from `risk.py`.
5. Never generate or reword the red-flag message, and never edit `src/copy/red_flag.json`. A human writes it, and it changes only after human review.
6. Never invent forecast data, cooling points or user quotes, including in tests, fixtures, the README or demo scripts. Use real API responses or clearly labelled fixtures.
7. The app displays; it does not decide. No band, temperature, time or safety text is computed, rounded differently or reworded in the frontend. It shows what the API returned.

### Code conventions

8. Backend: Python 3.11, type hints on all functions, standard library plus `boto3`, `requests` and `strands-agents` only, unless the team agrees otherwise.
9. App: TypeScript with React, Vite and Capacitor (core, Android, and the geolocation, share and filesystem plugins), plus the bundled Anek Devanagari typeface (`@fontsource-variable/anek-devanagari`), only, unless the team agrees otherwise.
10. All config comes from the environment variables listed in this brief. Never hard-code ARNs, account IDs, model IDs or API URLs. Nothing secret goes into the app bundle, and the signing keystore never goes in the repo.
11. All times are timezone-aware in `Asia/Kolkata`. Store dates as `YYYY-MM-DD` and hours as `HH:MM`.
12. No user-facing text inside `.py` or `.tsx` files. Backend fixed text goes in `src/copy/*.json`; UI text goes in `web/src/copy/*.json`, keyed by name, in both languages.
13. Write pytest tests for any logic in `risk.py`, `guard.py`, `forecast.py`, `cooling.py` and `api.py` routing and validation. Before saying a backend task is done, run `ruff check .` and `pytest`; before saying an app task is done, run `npm run lint` and `npm run build` inside `web/`. CI runs the same commands on every pull request.
14. `api` always answers in JSON with an error code, never a stack trace, and logs errors to CloudWatch with the `site_id`. `planner` sets the plan status to `failed` on any error.

### Working together

15. Before changing a shared interface (API routes or fields, tool signatures, table attributes, the `planner` payload), state the change and wait for the human to confirm with the other owners.
16. Keep commits small, with messages like `risk: add direct-sun band bump`. `main` is protected: nobody can push to it directly. Pull `main`, work on a branch, push the branch and open a pull request. It can be merged once the "All checks" status is green; no approval is needed.
17. After the Saturday 12:00 IST feature freeze, make bug fixes only.

## Definition of done

The project is submittable when every box is ticked.

- [ ] A new user on an Android phone outside the team downloads the app from our link, installs it, completes setup and gets a plan, in Hindi and in English
- [ ] The same flow works from the web link in a phone browser
- [ ] Replay mode produces a plan for the chosen May 2025 Jaipur date, with a stop-work window
- [ ] The red-flag message appears on every Danger-or-worse plan, word for word from `src/copy/red_flag.json`
- [ ] "Make crew voice note" returns a Hindi voice note that plays in the app and shares to WhatsApp
- [ ] The output guard falls back to the template plan when it detects an invented number (tested)
- [ ] `pytest` passes and `npm run build` passes; deployed with `sam deploy`, no manual console changes
- [ ] Public repo with README: problem, user, architecture, every AWS service used, setup, the download link, Open-Meteo attribution (CC BY 4.0)
- [ ] Video at or under 3:00: problem, the app on a real phone, voice note, where AWS fits, impact
- [ ] All four members verified on Builder Center; submitted at least 3 hours before the deadline

## Out of scope

Do not build any of the following before the deadline: a Play Store listing, an iOS or desktop build, Rust or any second backend language, chat-app or SMS integration, push notifications, offline mode, user accounts or login, more than one site per phone, maps, any symptom checker or medical advice beyond the fixed red-flag text, ML model training, air-quality data, or support for cities other than Jaipur in the demo.

## Glossary

| Term | Meaning |
|---|---|
| Heat index | How hot it feels to the body, from air temperature and humidity; assumes shade |
| Band | One of five risk levels from `SAFE` to `EXTREME_DANGER`, set only by `risk.py` |
| Stop window | Longest continuous run of Danger-or-worse hours within the shift |
| Replay mode | Running the plan on a past date using historical weather, for the demo |
| Red-flag message | Fixed, human-reviewed heat-stroke warning shown on dangerous days |
| APK | The Android app file a supervisor downloads and installs |
| Capacitor | The tool that wraps our React app into that APK |

## Sources

- Hackathon rules and judging
- NOAA WPC: The Heat Index Equation
- NWS heat index categories (table citing NOAA NWS)
- IMD heatwave criteria (secondary summary; confirm on IMD's site)
- Strands Agents SDK
- Amazon Polly available voices
- Open-Meteo
