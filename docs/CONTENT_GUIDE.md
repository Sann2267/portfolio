# Content Guide

How the portfolio's content is stored, validated, and extended. Everything a visitor reads
comes from `content/`; the templates only render what the models provide.

| | |
|---|---|
| Status | Current as of the Phase 10 release. Everything here is enforced by the loader and the test suite. |
| Validate | `.venv\Scripts\python -m app.content` (exit code 1 and a file/field message on any error) |
| Tests | `.venv\Scripts\python -m pytest` |

---

## 1. Layout

```text
content/
├── taxonomy.yaml                categories, technology groups, technologies and aliases
├── profile/
│   ├── profile.yaml             name, headline, focus, specializations, contacts
│   └── intro.md                 dossier introduction (Markdown)
├── skills/skills.yaml           skill groups; cases per skill are derived, never typed
├── timeline/timeline.yaml       site-wide events; case events live in each project
└── projects/<slug>/
    ├── project.yaml             structured metadata (schema below)
    └── case.md                  narrative sections split on "## " headings
```

Rules the loader enforces:

- Unknown keys are errors (`extra="forbid"`), so a typo never silently disappears.
- `slug` must equal the directory name; `id` is `case-NNN` and must match `case_number`.
- Every technology and AWS service must exist in `taxonomy.yaml` (names or aliases; the loader
  stores the canonical name). AWS services must belong to group `aws`.
- Every architecture edge must reference declared nodes; node `service` names must be in the
  taxonomy; `related_cases` and `related` must be real slugs.
- Evidence images (`src`) must exist under `static/` and carry `alt` text.
- `future_work` items must have `basis: planned` (or `not_documented`). A planned item can
  never be presented as done.

---

## 2. Adding a case

1. Create `content/projects/<slug>/` with `project.yaml` and `case.md`.
2. Pick the next `case_number` and matching `id`.
3. Use names from `taxonomy.yaml`; add missing technologies there first.
4. Put images under `static/images/projects/<slug>/` (WebP preferred) and reference them as
   `images/projects/<slug>/<file>.webp` with `alt`, `width`, and `height`.
5. Run `python -m app.content`. Fix anything it reports.
6. Run the tests. Nothing under `app/` or `templates/` needs to change.

---

## 3. `project.yaml` reference

```yaml
id: case-003                     # case-NNN
case_number: 3
slug: technodev-devops-cicd      # lowercase, hyphens, equals the directory name
title: TechnoDev DevOps CI/CD Platform
aliases: [DevOps Automation module]      # searchable alternative names
category: devops                 # primary category id from taxonomy
domains: [devops, cloud]         # category ids shown on the system monitor
project_type: CI/CD platform on AWS with self-hosted runners
status: completed                # completed | active | experimental | planned
role: >-                         # what you did; say what was provided by others
  DevOps engineer (module exercise) ...
context: >-                      # origin: competition module, personal project, team project
  LKS Nasional 2026 Cloud Computing ...
period:
  start: 2026-07                 # YYYY, YYYY-MM or YYYY-MM-DD, matching precision
  end: 2026-07                   # omit for ongoing
  precision: month               # day | month | year
  source: Public repository created 2026-07-27.
summary: >-                      # one paragraph, max 600 characters; used on cards and meta tags
  ...
technologies: [Docker, GitHub Actions]       # taxonomy names or aliases
aws_services: [Amazon VPC, AWS Lambda]       # taxonomy names with group aws
highlights: [...]                # key engineering decisions (claims, see 4)
challenges: [...]
solutions: [...]
results: [...]                   # only what the sources support
targets: [...]                   # numbers taken from a specification, e.g. RTO
future_work: [...]               # basis must be planned
evidence:                        # see 5
  - {kind: document, title: "...", basis: source}
repository: {status: public, url: https://github.com/..., label: "...", note: "..."}
demo: {status: unavailable, note: "..."}
documentation: {status: private, note: "..."}
architecture:                    # see 6
  groups: [...]
  nodes: [...]
  edges: [...]
timeline:                        # merged into /timeline with the case attached
  - {date: 2026-07-27, title: "...", basis: code}
related: []                      # optional manual override of related cases (slugs)
seo:
  description: "..."             # max 200 characters
  og_image: images/projects/<slug>/og.webp
```

`body` is never written in YAML; it is generated from `case.md`.

---

## 4. Claims and the honesty labels

`highlights`, `challenges`, `solutions`, `results`, `targets`, and `future_work` are lists of
claims. A plain string is a claim with `basis: source`. The long form adds where the statement
comes from:

```yaml
results:
  - "Three workflows are committed to the public repository."          # basis: source
  - {text: "314 offline tests.", basis: code}
  - {text: "Transmission delay under one second.", basis: source, note: "Reported in the deck; no log kept."}
  - {text: "Firmware implemented but not documented.", basis: user_statement}
targets:
  - {text: "RTO of 15 minutes or less.", basis: target}
future_work:
  - {text: "Telegram notifications.", basis: planned}
```

| basis | Rendered label | Use when |
|---|---|---|
| `source` | Documented | The module, deck, or README states it |
| `code` | Verified in code | The repository or workflow shows it |
| `user_statement` | Implemented in project environment | Built but not documented anywhere |
| `target` | Target from specification | A number the brief required, not a measurement |
| `planned` | Planned | Future work; never done |
| `not_documented` | Not documented | The outcome is unknown or evidence was not kept |

Never write a metric, uptime, accuracy value, client, or certification that no source supports.
When in doubt, use `not_documented`.

---

## 5. Evidence and links

```yaml
evidence:
  - {kind: architecture, title: "Module figure", basis: source}
  - {kind: screenshot, title: "Dashboard", src: images/projects/x/dash.webp, alt: "...", width: 1600, height: 900}
  - {kind: code, title: "Workflows", href: "https://github.com/.../workflows", basis: code}
  - {kind: document, title: "README", basis: code}
  - {kind: note, title: "The deck image is a stock dashboard, not this system"}
```

Kinds: `architecture`, `screenshot`, `diagram`, `log`, `document`, `code`, `demo`, `note`.

Link states (`repository`, `demo`, `documentation`) follow `SETTING.md`:
`public | private | archived | deleted | unavailable`. A link renders only when it is `public`
and has a `url`; otherwise the UI shows the state and the `note`. Never invent a replacement
repository.

The registry derives what evidence a case can show (`architecture`, `screenshots`,
`documentation`, `technical_breakdown`, `demo`, `code`) from these fields, so the UI never has
to guess.

---

## 6. Architecture diagrams

Diagrams are data. The Phase 07 renderer lays nodes out by group and draws the edges.

```yaml
architecture:
  groups:
    - {id: device, label: Device}
    - {id: cloud, label: AWS}
  nodes:
    - {id: esp32, label: ESP32, service: ESP32, group: device, description: "Reads the sensor, publishes JSON."}
    - {id: iot_core, label: AWS IoT Core, service: AWS IoT Core, group: cloud}
    - {id: telegram, label: Telegram alerts, service: Telegram Bot API, group: future, status: planned}
  edges:
    - {source: esp32, target: iot_core, label: MQTT publish, protocol: "MQTT over TLS, X.509"}
    - {source: iot_policy, target: iot_core, label: authorises, direction: none}
```

Node fields: `id`, `label`, `service` (taxonomy name), `category`, `status`, `group`,
`description`, `related_cases`. Node status: `implemented` (default), `planned`, `provided`
(supplied by a module or third party), `external`, `not_documented`. Edge fields: `source`,
`target`, `label`, `direction` (`forward`, `both`, `none`), `protocol`.

---

## 7. `case.md` sections

Text before the first `## ` heading is the intro. Each `## ` heading becomes one section:

| Heading | Rendered as |
|---|---|
| `## The Case` | The problem, context, and objective |
| `## Key Findings` | Important engineering decisions |
| `## Infrastructure`, `## Application`, `## Data`, `## Security`, `## Networking`, `## Observability`, `## Deployment` | Technical breakdown; only the headings you write are rendered |
| `## Result` | Source-supported outcome |
| `## Notes` | Anything else worth saying |

Any other heading is an error, which keeps the case renderer deterministic.

---

## 8. YAML gotchas

- Quote labels that contain commas or a colon followed by a space inside `{...}` mappings:
  `label: "claim jobs, logs, heartbeat"`.
- Quote values that look like numbers when they are text: `label: "port 5432"`.
- Dates are fine unquoted: `2026-08-11`, `2026-08`, and `2026` are all converted to strings.
- Use `>-` for long paragraphs; it folds lines and drops the final newline.

---

## 9. Profile, skills, timeline

- `profile.yaml`: `name`, `handle`, `headline` (max 160), `focus`, `location`, `languages`,
  `specializations` (category id, label, description), `contacts` (kind, label, url or value,
  `primary`). The introduction lives in `intro.md`.
- `skills.yaml`: groups with skills that list taxonomy names. The registry computes which cases
  demonstrate each skill; a skill with no case fails the tests, which keeps the skills page
  evidence-based.
- `timeline.yaml`: site-wide events. Case events go in the project's `timeline` list and are
  merged with the case slug attached.
