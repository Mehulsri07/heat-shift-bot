---
name: OpusCube (placeholder name)
description: A shade card for the working day. Each shift hour is one flat chip of colour with its risk band printed beside it.
colors:
  shell: "#1b3a93"
  on-shell: "#ffffff"
  on-shell-2: "#d3dbf6"
  shell-hover: "#2a4cae"
  safe: "#2e8b4e"
  caution: "#f0c22b"
  extreme-caution: "#ee7f1b"
  danger: "#d0302c"
  extreme-danger: "#5e0f1c"
  ground: "#f3f4f8"
  panel: "#ffffff"
  ink: "#12141c"
  ink-2: "#454b5e"
  rule: "#c9cdd9"
  rule-strong: "#9aa1b5"
  desk: "#dde0ea"
  tint: "#e7eaf5"
  placeholder: "#5d6377"
typography:
  figure:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: "37px"
    fontVariation: "'wdth' 84"
    fontFeature: "'tnum'"
  title:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.75rem"
    fontWeight: 750
    lineHeight: 1.2
    fontVariation: "'wdth' 86"
  headline:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 750
    lineHeight: 1.25
    fontVariation: "'wdth' 88"
  chip-code:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 750
    lineHeight: 1
    fontVariation: "'wdth' 80"
    fontFeature: "'tnum'"
  chip-name:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.125rem"
    fontWeight: 750
    lineHeight: 1.1
    letterSpacing: "0.01em"
    fontVariation: "'wdth' 76"
  body-large:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.5
  small:
    fontFamily: "'Anek Devanagari Variable', system-ui, 'Noto Sans Devanagari', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  none: "0"
spacing:
  grid: "8px"
  label-gap: "8px"
  pair-gap: "12px"
  gutter: "16px"
  page-top: "24px"
  section: "28px"
  row: "48px"
  shell-bar: "72px"
  stop-heading: "96px"
components:
  shell:
    backgroundColor: "{colors.shell}"
    textColor: "{colors.on-shell}"
    typography: "{typography.headline}"
    height: "72px"
    padding: "0 16px"
  day-tab:
    textColor: "{colors.on-shell-2}"
    typography: "{typography.body-large}"
    height: "48px"
  day-tab-selected:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
  language-switch:
    backgroundColor: "{colors.shell}"
    textColor: "{colors.on-shell-2}"
    height: "48px"
    padding: "4px 12px"
  language-switch-hover:
    backgroundColor: "{colors.shell-hover}"
  language-switch-selected:
    backgroundColor: "{colors.on-shell}"
    textColor: "{colors.ink}"
  hour-chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.chip-name}"
    rounded: "{rounded.none}"
    height: "48px"
  segmented:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    height: "52px"
    padding: "6px 12px"
  segmented-hover:
    backgroundColor: "{colors.tint}"
  segmented-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.panel}"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.panel}"
    typography: "{typography.body-large}"
    rounded: "{rounded.none}"
    height: "56px"
    padding: "12px 16px"
  button-primary-hover:
    backgroundColor: "{colors.shell}"
  button-primary-disabled:
    backgroundColor: "{colors.rule}"
    textColor: "{colors.ink-2}"
  button-quiet:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    height: "56px"
    padding: "12px 16px"
  button-quiet-hover:
    backgroundColor: "{colors.tint}"
  button-link:
    textColor: "{colors.shell}"
    height: "44px"
  button-link-hover:
    textColor: "{colors.ink}"
  input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body-large}"
    rounded: "{rounded.none}"
    height: "52px"
    padding: "10px 12px"
  notice:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "12px 14px"
  red-flag:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body-large}"
    rounded: "{rounded.none}"
    padding: "12px 14px 14px"
---

# Design System: OpusCube (placeholder name)

## Overview

**Creative North Star: "The Shade Card"**

The working day is laid out like a paint-shop shade card. Every shift hour is one chip: a flat field of enamel colour joined to a white label that carries a condensed code (the hour), the printed shade name (the risk band) and a tabular figure (the temperature). Read top to bottom, the strip shows the day changing colour, and a black bar in the left gutter brackets the hours when outdoor work stops. The card sits on a pale card-stock ground under an ultramarine shell that holds the site name, the language switch and the day tabs.

The system is built for one reader: a site supervisor holding an Android phone in direct sunlight. That decides everything. Type is large and heavy, colour is opaque and never blended, edges are hard, and every control is a standard one drawn square. It is dense where the day is (eleven 48px rows fit a 360 by 800 screen with the shell and the stop-work heading above them) and plain everywhere else. It does not look like a weather app (no suns, clouds, sky gradients or forecast cards) and it does not look like an office dashboard (no metric tiles, no charts).

The app displays; it never decides. Every band, temperature, time and line of safety text on screen is what the API returned, shown without recomputing, rounding or rewording. The design system styles those values. It has no say over them.

**Key Characteristics:**
- One strip of paint chips is the product; everything else on the plan screen supports reading it.
- Five flat band colours that mean risk and nothing else, under one ultramarine shell that is deliberately off that scale.
- Square corners, flat colour, hairline and ink rules. No gradients, no shadows.
- One typeface for Devanagari and Latin, condensed with its width axis so long band names fit a phone row.
- Every band reads without colour: its name and temperature are printed as text on each chip.
- An 8px vertical grid for the shell and the strip, so 1px rules stay one even weight on real phones.

## Colors

Black ink on card stock, one ultramarine shell, and five opaque enamels that only ever mean risk.

### Primary
- **Ultramarine Shell** (`shell`): the header behind the site name, language switch and day tabs; also the focus ring, link text, text caret, the loading sweep bar, the hover state of the primary button, and the browser theme colour. It is the one hue off the risk scale, chosen so that nothing in the app's own furniture can be mistaken for a band.
- **Shell White** (`on-shell`) and **Shell Mist** (`on-shell-2`): text on the shell. Mist is for the unselected tabs and language option; white is for the title and hover.
- **Shell Lift** (`shell-hover`): hover fill for the unselected language option.

### Secondary: the five bands
In order, as the API names them. The app assigns a colour only by reading the `band` field on an hour.
- **Safe Green** (`safe`): `SAFE`.
- **Caution Yellow** (`caution`): `CAUTION`.
- **Extreme-Caution Orange** (`extreme-caution`): `EXTREME_CAUTION`.
- **Danger Red** (`danger`): `DANGER`, and the solid bar across the top of the red-flag warning, which the API sends only on a Danger-or-worse day.
- **Extreme-Danger Maroon** (`extreme-danger`): `EXTREME_DANGER`. The darkest chip; it reads as the end of the scale by depth, not by brightness.

### Neutral
- **Ink** (`ink`): all primary text, 2px control borders, the selected segment, the primary button, the stop-work bracket and the current-hour outline.
- **Second Ink** (`ink-2`): supporting text (ledes, hints, sub-labels, the cooling-point type, the source line).
- **Card Stock** (`ground`): the page ground, tinted slightly toward the shell. The selected day tab takes this colour so it reads as a piece of the card below it.
- **Label White** (`panel`): the label half of every chip, inputs, quiet buttons, the red-flag box.
- **Strip Rule** (`rule-strong`): the 1px line between chips. It is darker than the ordinary rule because it has to survive sunlight.
- **Rule** (`rule`): dividers in the cooling-points list, the loading track, blank-chip fields and rules, disabled button fill.
- **Desk** (`desk`): what shows either side of the 30rem column on a wide screen.
- **Tint** (`tint`): hover fill for white segments and quiet buttons, and the highlight behind selected text.
- **Placeholder** (`placeholder`): input placeholder text.

### Named Rules
**The Reserved Scale Rule.** The five band colours belong to the risk bands. They colour an hour's chip field, and Danger Red marks the fixed red-flag warning. They are never used for buttons, links, headings, selection states, decoration or branding inside the app.

**The Off-Scale Shell Rule.** Anything the app needs to colour for its own purposes (focus, links, progress, the header) uses Ultramarine Shell or ink. If a new element seems to want green, yellow, orange or red, it is either a band or it is ink.

**The Name In Print Rule.** No band is ever shown by colour alone. Its name and its temperature are printed as text on the same row.

In the product, band colours appear in exactly two places: the colour field of an hour chip and the top bar of the red-flag warning. Text selection uses Tint and the error notice is outlined in ink.

## Typography

**Display, body and label font:** Anek Devanagari Variable (fallbacks: system-ui, Noto Sans Devanagari, sans-serif). Self-hosted from the `@fontsource-variable/anek-devanagari` package using its width-axis file (`wdth.css`), so the APK needs no network for type.

**Character:** One family carries Devanagari and Latin at matched weight and height, so Hindi and English are equal on every row. Hierarchy comes from weight (400 to 800) and from the width axis (76% to 92%), not from a second typeface.

### Hierarchy
- **Figure** (800, 2rem, 37px line, width 84%, tabular): the stop-work times in the heading above the strip. The largest text in the app.
- **Title** (750, 1.75rem, 1.2, width 86%): the setup screen's heading.
- **Headline** (750, 1.25rem, 1.25, width 88%): section headings under the strip, loading and failed titles, the "no stop window" line, the shell title (700), the red-flag heading (800).
- **Chip code** (750, 1.25rem, line 1, width 80%, tabular): the hour on each chip. The temperature uses the same width and tabular figures at 1.125rem, weight 650, right-aligned.
- **Chip name** (750, 1.125rem, 1.1, width 76%, 0.01em, uppercase): the band name on each chip in Latin. In Hindi it widens to 84%, drops the letter-spacing and opens to 1.25 line height.
- **Body large** (400, 1.125rem, 1.55, max 65ch): the plan text. Also the size for inputs, buttons (700, width 92%), day tabs (700, width 88%) and the red-flag text (600, line 1.5).
- **Body** (400, 1.0625rem, 1.5): default text, ledes and hints.
- **Label** (700, 1.0625rem): field labels and legends; segments use 600.
- **Small** (0.875rem): sub-labels (600), field notes, the cooling-point type, the source line, the current-hour tag (700).

### Named Rules
**The One Family Rule.** Anek Devanagari sets everything in both scripts. No second typeface, no monospace for figures; tabular figures come from the same font.

**The Joined Letters Rule.** Devanagari is never letter-spaced and never relies on capitals. Any style that uses uppercase or tracking for Latin needs a `:lang(hi)` counterpart that removes both and gives the line more height.

**The Width Does The Work Rule.** When text must fit a narrow column, narrow it with the width axis (no lower than 76%) before shrinking it. Nothing in the app is set below 0.875rem.

## Layout

A single column, mobile-first and portrait, capped at 30rem and centred on the desk colour on anything wider. There are no breakpoints; the phone layout is the layout.

Horizontal rhythm is a 16px gutter. The strip ignores the gutter and runs edge to edge. Vertical gaps between form fields and between sections under the strip are 28px; label to control is 8px; paired fields (latitude and longitude, shift start and end) sit in two equal columns 12px apart. The setup page opens 24px below the shell.

The shell and the strip sit on an 8px grid: shell bar 72px, day tabs 48px, stop-work heading 96px, every hour row 48px. That gives 744px for an eleven-hour shift, inside an 800px-tall phone.

Each hour row is a five-column grid: a 10px rail for the stop-work bracket, the colour field at 22% of the width (inset 4px from the rail), the hour at 3.7rem, the band name taking the remaining space, and the temperature at its natural width with 12px to the right edge. The stop-work heading uses the same 10px rail so its ink bar lines up with the bracket below.

Touch targets: 56px buttons, 52px inputs and segments, 48px tabs and language options, 44px text links. Safe-area insets pad the top of the shell and the bottom of the footer.

### Named Rules
**The Eight Grid Rule.** Rows, the shell bar, tabs and the stop-work heading are multiples of 8px tall. Phones scale CSS pixels by 2.625, 2.75 or 3, and only multiples of 8 land on whole device pixels at all three, which keeps every 1px rule the same weight and the bracket unbroken. A new element placed above or inside the strip must keep to it.

**The Strip First Rule.** On the plan screen the full shift is visible without scrolling on a 360 by 800 phone. Nothing is inserted between the shell and the strip except the stop-work heading.

## Elevation & Depth

Flat. There are no shadows, no gradients, no blurs and no translucent layers. The only alpha value in the system is the 12% white hover on an unselected day tab.

Depth is stated by adjacency and line. The selected tab shares the card's colour and so joins it. Surfaces are separated by a 1px rule or a 2px ink border. Emphasis is a heavier border (3px on the red-flag box and the current-hour outline) or a solid ink fill, never a lift.

### Named Rules
**The Flat Enamel Rule.** Colour is one opaque value per surface and is never blended, tinted, faded or overlaid. A band colour at reduced opacity is a different, undefined colour and is not allowed.

## Shapes

Square corners everywhere (radius 0), including inputs, buttons, the native audio player and the favicon. Edges are hard.

Line weights have fixed jobs: 1px for rules between rows and list items, 2px ink for control borders and the gap between joined segments, 3px for the red-flag border, the current-hour outline and the focus ring. Underlines on text links are 2px, offset 4px.

Recurring forms are the rectangle and the bar: the chip's colour field, the 10px ink bracket, the 16px red bar on the warning, the 10px loading track. There are no icons, illustrations or pictograms in the app's own markup; the only glyphs are the browser's native time and date pickers.

## Components

Standard controls throughout, drawn square in ink and white. Nothing is custom where a native element exists: tabs and switches are real radio inputs, the date and time fields are native, the player is the browser's `<audio>`.

### Hour chip (signature)
One row per shift hour, 48px minimum, white label with a 1px Strip Rule between rows. From the left: the rail, the band colour field, the hour, the band name, the temperature.
- **Band colour:** set only from the hour's `band` value. A row with no band (the blank loading card) shows Rule grey.
- **Stop-work bracket:** rows inside the stop window fill their rail with ink. Each rail overlaps the rule above it by 1px, so the bar is unbroken down the stopped hours. The band name also carries a screen-reader-only "stop" mark.
- **Current hour:** on today's strip only, the row gets a 3px ink outline set inside its edge and a small white tag over the colour field. This is the one moving part.
- **Arrival:** when a plan loads, each colour field wipes in from the left once (520ms, staggered 30ms per row). Removed under reduced motion.

### Stop-work heading
Sits directly above the strip and is its key: a 10px ink bar on the left (the same bar as the bracket), a one-line label, and the start and end times at Figure size. When there is no stop window, the bar is absent and a single Headline-size line says so.

### Red-flag warning
The fixed heat-stroke message. A white box with a 3px ink border, a solid 16px Danger Red bar across the top, an 800-weight heading and the text at Body large, weight 600. The text is shown exactly as the API sent it, with its line breaks. It appears directly after the plan text.

### Shell
Ultramarine, full width. A 72px bar with the site name (up to two lines, then clipped) and the language switch; on the plan screen, a 48px row of day tabs beneath. Focus rings inside the shell are white.
- **Day tabs:** equal columns, Shell Mist text on the shell. Hover lightens the tab and whitens the text. The selected tab is filled with Card Stock and set in ink.
- **Language switch:** two joined blocks in a 2px white frame. Unselected is shell-coloured with Shell Mist text (weight 500); selected is white with ink text (weight 800).

### Segmented choice
Two or three joined blocks in a 2px ink frame with a 2px ink line between them, each at least 52px tall. Unselected is white with ink text; hover is Tint; selected is solid ink with white text. Used for language on setup and the direct-sun question.

### Buttons
- **Shape:** square, full width, 56px minimum, 2px ink border, 12px by 16px padding.
- **Primary:** solid ink with white text (700, width 92%). One per section: save the site, make the voice note, share it.
- **Hover / active / focus:** fill and border turn Ultramarine Shell over 160ms; pressing nudges it down 1px; focus is the 3px shell ring, 2px off the edge.
- **Disabled:** Rule grey fill and border with Second Ink text.
- **Quiet:** white with ink text and the same ink border; hover is Tint. For secondary actions: use my location, retry.
- **Link:** underlined Ultramarine text (600) with a 44px hit height; ink on hover. For the footer actions and the fallback audio link.

### Inputs
White, 2px ink border, square, 52px minimum, text at Body large. Numeric, time and date fields use tabular figures at weight 600. Labels sit above at weight 700; sub-labels for paired fields are Small, weight 600, in Second Ink. Hints sit below in Small. Focus is the shell ring.

### Lists
Cooling points are a ruled list: 1px Rule above and below each item, name (650) on the left, distance (700, tabular) on the right, type beneath in Small.

### States
- **Loading:** a Headline-size line, a hint, a 10px Rule-grey track with an Ultramarine bar sweeping across it (1.5s), and the blank card: as many empty chips as the shift has hours, with grey fields and lighter rules. Under reduced motion the bar sits still at 40% width.
- **Failed:** the error sentence at Headline size and a quiet retry button.
- **Error notice:** a white box with a 2px ink border, ink text at weight 600, 12px by 14px padding, placed directly above the button it relates to.

### Motion
One easing (`cubic-bezier(0.16, 1, 0.3, 1)`). Three uses: the chip wipe on arrival, the loading sweep, and 160ms colour changes on buttons and segments. All three stop under `prefers-reduced-motion`.

## Do's and Don'ts

### Do:
- **Do** colour an hour only from the `band` value the API returned, and print that band's name and temperature as text on the same row.
- **Do** use Ultramarine Shell or ink for anything the app itself needs to colour: focus, links, progress, headers, selection states.
- **Do** keep every corner square and every colour flat and opaque.
- **Do** keep the shell bar, tabs, stop-work heading and hour rows on multiples of 8px, and keep the full shift visible without scrolling on a 360 by 800 phone.
- **Do** set everything in Anek Devanagari, and narrow text with the width axis (down to 76%) before making it smaller.
- **Do** give any uppercase or letter-spaced Latin style a `:lang(hi)` counterpart with no tracking and more line height.
- **Do** keep the red-flag warning as it is built: 3px ink border, solid Danger Red bar, heavy type, its text shown word for word.
- **Do** use native controls (radio inputs, date and time fields, `<audio>`) drawn square, with touch targets of at least 44px.
- **Do** respect `prefers-reduced-motion` for every animation.

### Don't:
- **Don't** use a band colour for a button, link, heading, badge, illustration or any decoration.
- **Don't** blend, tint, fade or overlay a band colour, and don't add gradients or shadows anywhere.
- **Don't** show a band by colour alone.
- **Don't** compute, round or reword a band, temperature, time or safety text in the app; show what the API returned.
- **Don't** soften, shorten, collapse, shrink or restyle the red-flag warning into something easy to miss.
- **Don't** add suns, clouds, sky gradients or forecast cards, and don't add metric tiles or charts.
- **Don't** round corners, including on inputs, buttons and the audio player.
- **Don't** letter-space Devanagari or set any text below 0.875rem.
- **Don't** treat the yellow FIXTURE DATA banner or the `?fixture=` modes as product design. They exist only when `VITE_FIXTURES=1` and never ship.
