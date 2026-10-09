---
version: 1
slug: "web-src-app-tsx"
primary_target: "web/src/App.tsx"
related_targets: ["web/src/screens"]
---

# Surface brief: the app (setup and plan screens)

Scope: `web/src/App.tsx` and `web/src/screens/`. Mode: Operate. Mobile-first, portrait, on an Android phone in direct sunlight.

Audience and job: a site supervisor reads the shape of the working day hour by hour and decides the shift. Field readability beats visual impact. Must not read as a weather app or a SaaS dashboard.

Unresolved: the app's name (placeholder `OpusCube`); the wording of the DANGER action; the red-flag text is not written yet.

## Direction contract

THESIS: The day is a shade card. Every shift hour is one flat chip of colour with its name printed underneath, so the whole day reads as a strip of paint chips. It refuses the forecast card with sun icons and sky gradients, and the dashboard of metric tiles.

OWN-WORLD: Paint-shop shade cards. A light card ground, black ink, and an ultramarine shell that sits off the risk scale. Five opaque enamel band colours from green through yellow, orange and red to deep maroon, always flat, never blended. Each chip is a colour field joined to a white label panel carrying a condensed code (the hour), the shade name (the band) and a tabular figure (the temperature). Square corners, hard edges, hairline rules. Standard controls throughout: tabs, inputs, buttons.

STORY: The supervisor opens the app, sees the run of chips change colour down the shift, reads where the stop-work bracket starts and ends, reads the short plan, and sends the voice note to the crew.

FIRST VIEWPORT: Ultramarine header with the site name and the Today and Tomorrow tabs. Directly beneath, the full shift as one column of full-width chips, eleven rows for a 07:00 to 18:00 shift, all visible without scrolling on a 360 by 800 phone. Each row: colour field on the left, then hour, band name and temperature on the white label. A bracket in the left gutter spans the stop-work hours and carries their start and end times. The plan text, red-flag box, cooling points and the voice note action follow below.

FORM: Shade card, position 6 on the grounded list. Signature move: the hour strip as paint chips with printed names, plus one moving part, the marker for the current hour on today's strip. Seed key 06ec451c.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Adaptations recorded after the first finish review

- **Stop times live in the heading, not on the bracket.** The contract put the start and end times at the bracket's two ends. A 10px gutter cannot carry readable times in sunlight, in Devanagari or Latin, without rotated or very small type. The times are set at figure size in the heading directly above the strip, and the same ink bar sits beside that heading as the bracket's key. Reason: the user's answer that field readability wins.
- **Three day tabs and a language switch in the shell.** The contract named Today and Tomorrow; the original request also asks for a past date (replay) and a Hindi and English toggle.
- **A scale of all five bands** closes the plan screen, so a day that shows only two colours can be placed on the full card.
- **Order under the strip** follows PLAN.md: plan text, red-flag warning, cooling points, voice note.
