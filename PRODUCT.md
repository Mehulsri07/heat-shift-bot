# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary user is a construction-site supervisor or contractor in Rajasthan who sets shift timing for 20 to 50 workers. They use an Android phone, outdoors, often in direct sunlight, and need to decide which hours the crew works tomorrow or today.

The workers are a secondary audience who never see the app. They receive the plan as a short Hindi voice note in the crew's WhatsApp group.

## Product Purpose

Turn an hourly heat forecast into a shift decision for one site: which hours are safe, which need breaks, and when outdoor work stops. Success is a supervisor who opens the app, reads the shape of the day hour by hour in a couple of seconds, and forwards the voice note to the crew.

## Positioning

A deterministic, tested risk engine decides every band, temperature and time. The AI model only words what the engine returns, and the app only displays what the API returns. A weather app gives a forecast; this gives a work instruction for a specific site and shift.

## Operating Context

- One setup form per site: language, location, site name, shift hours, direct sun or not. No login.
- A plan screen for Today and Tomorrow, plus a past date for replaying a real heat day in the demo.
- A crew voice note, always in Hindi, shared through the Android share sheet.
- Ships as an Android APK (React wrapped with Capacitor) and as the same web link.
- Plans are built in the background; the app polls and must show loading, failed and retry states.

## Capabilities and Constraints

- Five risk bands, in order: SAFE, CAUTION, EXTREME_CAUTION, DANGER, EXTREME_DANGER.
- Each hour arrives from the API with its time, temperature, humidity, heat index and band.
- The stop-work window, plan text, cooling points and audio link all come from the API.
- The app never computes, rounds or rewords a band, temperature, time or safety text.
- The red-flag heat-stroke message is fixed, human-written text. It is shown word for word whenever the API sends it.
- Every UI string lives in `web/src/copy/hi.json` and `en.json`; none in component files.
- React, Vite and TypeScript with plain CSS. No router, UI kit, state library or CSS framework.
- Undecided: the app's name (placeholder `OpusCube`), and the wording of the DANGER action.

## Brand Commitments

- Must not look like a weather app: no suns, clouds, sky gradients or forecast cards.
- Must not look like a SaaS dashboard: no metric cards and charts built for an office laptop.
- When field readability and visual impact pull apart, field readability wins.

## Evidence on Hand

- Real hourly weather for Jaipur on 20 May 2025 from Open-Meteo (peak 42.4°C), fetched through `src/forecast.py`.
- The band thresholds and action lines in `PLAN.md`.
- No user interviews, testimonials or usage numbers exist. Do not quote or paraphrase any user.
- The red-flag wording does not exist yet; it will be supplied in `src/copy/red_flag.json`.

## Product Principles

1. The hour-by-hour day is the product. Everything else on the plan screen supports reading it.
2. Display, never decide. What the engine said is what the supervisor sees.
3. Built for a phone in the sun, held by someone who is busy.
4. Voice carries the plan to people who will not read it.
5. The fixed safety warning is never softened, shortened or restyled into something easy to miss.

## Accessibility & Inclusion

- Every band is readable without colour: its name and temperature appear as text.
- Hindi (Devanagari) and English are equal first-class languages.
- High contrast and large type for bright sunlight; large touch targets.
