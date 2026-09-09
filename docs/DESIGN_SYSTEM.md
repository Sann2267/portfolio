# Design System

Theme: a modern detective investigation room crossed with a cloud operations control room.
Dark, restrained, technical, readable. The visual metaphors (case files, evidence pins, board
grid, terminal panel, status lights, timestamps) are carried by components; no page hardcodes
colours or spacing.

## Files

| File | Role |
|---|---|
| `static/css/tokens.css` | Every custom property. The only file allowed to contain raw colour values. |
| `static/css/base.css` | Reset, typography, links, code, tables, layout primitives, focus ring, motion classes, reduced-motion override. |
| `static/css/components.css` | One block per component macro. |
| `static/css/room.css` | Home page composition (Phase 05). |
| `static/css/case.css` | Case file layout and architecture diagram (Phases 06 and 07). |
| `templates/partials/sprite.svg` | Inline SVG symbols, included once per page and referenced with `<use href="#i-...">`. |
| `templates/components/*.html` | Jinja macros. They take plain values (hrefs, labels) so they render outside Flask too. |

## Tokens

- Surfaces: `--color-background`, `--color-background-deep`, `--color-surface`,
  `--color-surface-elevated`, `--color-surface-overlay`, `--color-border`, `--color-border-strong`.
- Text: `--color-text-primary` (warm off-white), `--color-text-secondary`, `--color-text-muted`,
  `--color-text-inverse`.
- Accents, used sparingly: `--color-accent-active` (amber: active investigation, highlighted
  evidence), `--color-accent-success` (green: verified, operational), `--color-accent-warning`
  (orange: caution, targets), `--color-accent-danger` (red: failed, security). Each has a
  `--tint-*` at 14% for backgrounds.
- `--shadow-sm/md/lg/glow`, `--radius-sm/md/lg/pill`, `--space-1` … `--space-10`,
  `--text-xs` … `--text-3xl`, `--font-sans` and `--font-mono` (system stacks, no webfonts),
  `--dur-fast/base/slow/trace` with `--ease` and `--ease-out`.

## Components

| Macro | File | Purpose |
|---|---|---|
| `nav(links, active, …)` | `nav.html` | Sticky header with brand, primary links, search/palette trigger, mobile toggle. |
| `case_card(project, href, …)` | `case_file.html` | Evidence card for a case: id, status light, category, title, summary, technology badges, evidence tags. Carries `data-tech` and `data-slug` for board highlighting. |
| `evidence_card(item, static_url)` | `case_file.html` | Screenshot, diagram, document, or code reference with optional image. |
| `tech_badge`, `badge_list`, `evidence_tag`, `status_indicator`, `claim_label`, `claim_list` | `badges.html` | Small labels. `claim_label` renders the honesty basis when it is not `source` or `code`. |
| `terminal_panel(lines, title, typing)` | `panels.html` | Monospace key/value log with status tones. |
| `technical_note(title, body, tone)` | `panels.html` | Sticky-note style callout. |
| `metric_card(label, value, note, tone)` | `panels.html` | System monitor tile. |
| `panel`, `section` | `panels.html` | Wrappers using `{% call %}`. |
| `timeline_node(event, case_title, case_href)` | `timeline.html` | One event on the timeline rail. |
| `link_or_state(link, label)` | `links.html` | Anchor only when the link is public; otherwise the availability state and note. |
| `modal`, `drawer`, `command_palette` | `overlays.html` | Native `<dialog>` modal, node-detail drawer (floats on small screens), Ctrl+K palette shell. |

Architecture nodes and edges are rendered by the diagram macro added in Phase 07.

## Motion

Classes: `.reveal` (+ `--1` … `--4` delays), `.slide-in`, `.fade`, `.trace` (SVG line
tracing), `.cursor` (terminal caret), `.evidence-highlight` (pulse). All durations come from
tokens. Under `prefers-reduced-motion: reduce` every animation and transition collapses to
0.001 ms and traced lines render complete.

## Rules

1. Technical content has priority; effects never cover text.
2. Every interactive element is a real link or button with a visible focus ring.
3. Hover-only behaviour always has a focus or touch equivalent.
4. No inline styles and no raw colours in templates (enforced by `tests/test_design_system.py`).
5. Prefer a new macro over page-specific markup.
