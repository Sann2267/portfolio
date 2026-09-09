# Architecture — Detective Case Room Portfolio

| | |
|---|---|
| Phase | 02 — Content model complete (Phase 01 audit and architecture retained below) |
| Status | Content layer implemented in `app/models` and `app/content`; see `docs/CONTENT_GUIDE.md`. Design system begins in Phase 03. |
| Audit date | 2026-09-09 |
| Owner | Ibnu Adzim (GitHub `Sann2267`) |
| Governing specs | `00_MASTER_BUILD.md` … `10_VERIFICATION_AND_RELEASE.md`, `SETTING.md` |

This document is the single reference for how the portfolio is built. Later phases refine the
content schema and UI, but they do not change the layering, folder layout, or principles below unless
a conflict is found and recorded in the decision log at the end.

Guiding rule, inherited from the master build:

> CONTENT != UI. A project is content. A project page is a renderer.

---

## Current architecture

### Repository state at audit

The directory `c:\Ibnu\project\portofolio` was not a git repository and contained no application code.
It held only the build specification and the source material:

| Item | Found |
|---|---|
| Phase specs | `00_MASTER_BUILD.md`, `01_…` through `10_…` (11 files) |
| Conventions | `SETTING.md` (source-code availability states), `README.md` (Indonesian build instructions plus content-schema fragments) |
| Source PDFs | 4 files (moved to `docs/sources/`, ignored by git) |
| Python code, templates, CSS, JS, images | none |
| Tests, CI, deployment config | none |
| Package manager files | none |
| Git history | none (the previous repository was deleted) |

Because nothing existed, there is no legacy structure to migrate. The phase spec files stay at the
repository root until Phase 10 so that the prompts that reference them by path keep working; Phase 10
relocates them to `docs/build/`.

### Toolchain available on the build machine

| Tool | State | Consequence |
|---|---|---|
| `python` on PATH | 3.10.6 (laragon) | Never use bare `python`. |
| `py -3.12` | CPython 3.12.5 | The interpreter for this project. `.python-version` pins `3.12`. |
| `uv` | 0.11.18 | Preferred for creating the venv and running tools: `uv venv --python 3.12`, `uv pip install -r …`. |
| `pip` | 26.1 | Fallback. |
| `poetry` | not installed | Not used. |
| Node.js | 24.x installed | Not required. Permitted only as optional dev tooling (see Asset strategy). |
| git | 2.52 | Global identity is a different account; this repo sets its own (see Deployment strategy, repository section). |
| `gh` | 2.100, authenticated as `Sann2267` | Used for repository creation and for reading source repositories without cloning. |
| PDF tooling | `pdfplumber 0.11.10` + `pypdfium2` + `Pillow` under `py -3.12` | Text extraction and page rasterization with no extra installs. |

### Source material

| File (in `docs/sources/`) | Pages | Text layer | Notes |
|---|---|---|---|
| `Modul - DevOps Automation.pdf` | 18 | ~41.7k chars | LKS National Competition module, "TechnoDev" scenario. Architecture figure (p6) is an image. |
| `Modul - Cloud Ai, Data Analytics.pdf` | 14 | ~31.4k chars | LKS National Competition module, "NusaCommerce" scenario. Pages 1 and 14 are images. |
| `Modul - Infrastructure as Service.pdf` | 14 | ~20.3k chars | "LKS Nasional 2026 Cloud Computing — Infrastructure Automation". Diagram page 7 partly image. |
| `Monitoring IoT ESP32 & AWS.pdf` | 13 | 0 chars | Every page is an image. Must be rasterized and transcribed visually. |

All three cloud modules are competition task briefs. TechnoDev and NusaCommerce are fictional scenario
companies defined by the brief. The portfolio must present those cases as competition or lab
implementations, never as client or production work.

### Existing code that serves as factual source

| Case | Local code | GitHub repository | Visibility | Content | `repository.status` |
|---|---|---|---|---|---|
| 001 Indonesia Job Data Scraping System | `c:\Ibnu\instagram\loker-search` | `instagram` | private | scraping pipeline (Python, curl_cffi, pydantic, OCR, pytest) | `private` |
| 002 Job Listing Fullstack Dashboard + API | `c:\Ibnu\project\dashboard` | `loker-dashboard` | private | FastAPI backend + Vite/React frontend | `private` |
| 003 TechnoDev DevOps CI/CD Platform | — | `devops-learner-lab` | public | GitHub Actions only: CI (flake8 + Docker builds of four Lambda images on PR), CD (ECR push, Lambda image update, Amplify deploy, API Gateway smoke test), runner verification. All jobs `runs-on: self-hosted`. Application trees referenced by the workflows are not in the repo. | `public` (partial) |
| 004 NusaCommerce Analytics Platform | — | `nusacommerce` | private | CloudFormation stacks, Lambdas, Glue ETL, EMR PySpark, Step Functions ASL, Redshift Spectrum SQL, WAF reference, Amplify dashboard. The README states the application code was provided as competition assets; the author's work is the infrastructure. | `private` |
| 005 Multi-Tenant SaaS Infrastructure | — | none found | — | PDF only | `unavailable` |
| 006 ESP32 + AWS IoT Monitoring | — | none linked | — | The presentation deck (13 slides) documents the design: DHT22 → ESP32 → Wi-Fi → AWS IoT Core (X.509, TLS, IoT policy, MQTT QoS) → Node-RED dashboard. The author states the firmware, IoT Core setup, and flow were implemented but never published. A public repository under a similar name is an AI-generated reconstruction using Mosquitto on EC2; it is not the documented implementation and is not linked. | `unavailable` |

Two consequences for later phases:

- The React frontend of case 002 is the *subject* of that case. The portfolio itself is Flask/Jinja.
- Case 006 rests on the deck plus the author's statement. Claims that only the author can vouch for
  carry `basis: user_statement` ("Implemented in project environment"); the deck's sub-second delay
  figure is quoted as reported, not measured; the three extensions in the deck are `planned`.

### Content conventions already defined by the specs

`SETTING.md` and `README.md` fix rules the content model must honour:

- Repository, demo, and documentation links are optional and carry a state:
  `public | private | archived | deleted | unavailable`.
- A link renders only when it is public and has a URL. Otherwise the UI shows the state label
  ("SOURCE CODE — Private") and leans on evidence instead.
- Evidence is a list of typed items (architecture, screenshots, documentation, technical breakdown,
  demo). Each evidence section renders only when present.
- Never upgrade a planned item to a completed one. Unknowns are labelled `Not documented`,
  `Implemented in project environment`, `Planned`, or `Future improvement`.

### Technical debt and inconsistencies found

1. The suggested target tree lists both `app.py` and a package `app/`. `import app` would resolve to the
   package and shadow the module. Resolution: the entry point is `wsgi.py`; there is no `app.py`.
2. `app/content/` (loader code) and `content/` (data) share a name. Both are kept; this document defines
   the first as code and the second as data.
3. Case titles differ between `00_MASTER_BUILD.md` and `02_CONTENT_MODEL.md` for cases 004 and 006.
   Resolution in Phase 02: each project has one `title` plus `aliases`, and search indexes both.
4. `README.md` mixes build instructions with schema fragments that duplicate `SETTING.md`. The fragments
   are folded into the content model in Phase 02; the README is rewritten in Phase 10.
5. An older public repository `Sann2267/portofolio` (2025, a student-era freelance README) predates
   this project. It is archived so it cannot be confused with the new `Sann2267/portfolio`.

---

## Proposed architecture

### Principles

1. Python-first: Flask + Jinja2 own routing, rendering, content loading, and business logic.
2. Content is data: every project is a folder of YAML and Markdown. The UI never hardcodes a project.
3. One renderer: `/projects/<slug>` renders every case through the same template and section list.
4. Progressive enhancement: every page is complete as server-rendered HTML. HTMX and small vanilla JS
   modules add interaction; they never gate content.
5. Honest content: the loader enforces link states and the review process enforces source-backed claims.
6. Small dependency surface: no database, no ORM, no forms library, no frontend framework, no build step.

### Layers

```text
┌──────────────────────────────────────────────────────────────┐
│ ROUTES        Flask blueprints: pages, projects, search       │  thin: parse request, call service, pick template
├──────────────────────────────────────────────────────────────┤
│ SERVICES      project · search · relation · diagram · seo    │  pure Python, unit-testable, no Flask imports
├──────────────────────────────────────────────────────────────┤
│ CONTENT       loader → validation → ContentRegistry          │  YAML + Markdown → pydantic models, loaded once
│ MODELS        Project, Evidence, Architecture, Profile, …     │
├──────────────────────────────────────────────────────────────┤
│ TEMPLATES     base → pages → components (macros) → partials  │  Jinja2; the only place HTML lives
├──────────────────────────────────────────────────────────────┤
│ STATIC        tokens.css + a few CSS files · htmx · 3 JS modules · images · icon sprite
└──────────────────────────────────────────────────────────────┘
```

### Stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Required by the master build; matches sibling projects. |
| Web framework | Flask 3.x, application factory | Small, explicit, Jinja built in. |
| Templates | Jinja2 macros + includes | Reusable components without a JS framework. |
| Structured content | YAML (`PyYAML`, `safe_load`) | Human-editable, comments allowed. |
| Narrative content | Markdown (`Markdown` package, `fenced_code`, `tables`, `toc`) | Long-form case text separate from metadata. |
| Validation | pydantic v2 | Fail fast at load time with file-and-field error messages; same library as sibling projects. |
| Interactions | HTMX (vendored, pinned) + vanilla JS modules | Server-driven partials; JS only for hover/focus/keyboard behaviours. |
| Styling | Plain CSS with custom properties | No build step; tokens enforce the visual language. |
| Server (prod) | Vercel Python runtime; gunicorn in Docker as the portable alternative | Matches the author's existing deployment habit. |
| Server (dev) | `flask run` via `py -3.12`/uv | |
| Tests | pytest + Flask test client | |
| Lint/format | ruff | One tool for both. |
| Not used | SQLAlchemy, WTForms, any database, any frontend framework, Node build tooling | No persistent data; contact page is links, not a form. |

### Domain model

Implemented in Phase 02 under `app/models/` and documented field by field in
`docs/CONTENT_GUIDE.md`. Two additions over the original sketch: every statement about a case is a
`Claim` with a `basis` (source, code, user_statement, target, planned, not_documented) that the UI
renders as a label, and architecture nodes carry a `status` (implemented, planned, provided, external,
not_documented) so components supplied by a competition module are marked as such. The original
sketch is kept below for reference.

```python
LinkStatus = Literal["public", "private", "archived", "deleted", "unavailable"]
ProjectStatus = Literal["completed", "active", "experimental", "planned"]
EvidenceKind = Literal["architecture", "screenshot", "diagram", "log", "document", "code", "demo", "note"]

class Link(BaseModel):            # repository / demo / documentation
    status: LinkStatus
    url: HttpUrl | None = None
    label: str | None = None

class Evidence(BaseModel):
    kind: EvidenceKind
    title: str
    src: str | None = None        # path under static/, validated at load
    alt: str | None = None
    caption: str | None = None
    width: int | None = None
    height: int | None = None

class ArchNode(BaseModel):
    id: str; label: str
    service: str | None = None; category: str | None = None
    status: Literal["implemented", "planned", "external", "not_documented"] = "implemented"
    group: str | None = None; description: str | None = None
    related_cases: list[str] = []

class ArchEdge(BaseModel):
    source: str; target: str
    label: str | None = None
    direction: Literal["forward", "both", "none"] = "forward"
    protocol: str | None = None

class Architecture(BaseModel):
    groups: list[ArchGroup] = []; nodes: list[ArchNode] = []; edges: list[ArchEdge] = []

class Project(BaseModel):
    id: str                        # "case-003"
    case_number: int               # 3
    slug: str                      # "technodev-devops-cicd"
    title: str; aliases: list[str] = []
    category: str; project_type: str
    status: ProjectStatus; role: str | None = None
    context: str | None = None     # e.g. "LKS Nasional 2026 — Cloud Computing module"
    summary: str                   # one paragraph for cards and meta description
    technologies: list[str] = []; aws_services: list[str] = []
    highlights: list[str] = []; challenges: list[str] = []; solutions: list[str] = []
    breakdown: dict[str, str] = {} # infrastructure / application / data / security / networking / observability / deployment → Markdown
    results: list[str] = []        # source-supported only
    future_work: list[str] = []    # explicitly planned items
    evidence: list[Evidence] = []; gallery: list[Evidence] = []
    architecture: Architecture | None = None
    repository: Link; demo: Link; documentation: Link
    timeline: list[TimelineEvent] = []
    related: list[str] = []        # optional manual override; otherwise derived
    body_html: str                 # rendered case.md
```

Profile, Skill, SkillGroup, and TimelineEvent models follow the same pattern and live in
`app/models/`. The exact field set is frozen in Phase 02 and documented in `docs/CONTENT_GUIDE.md`.

---

## Folder structure

```text
portofolio/                         git root → https://github.com/Sann2267/portfolio
├── wsgi.py                         app = create_app()  — Flask and Vercel entry point
├── config.py                       BaseConfig / DevelopmentConfig / ProductionConfig / TestingConfig
├── requirements.txt                runtime: Flask, PyYAML, pydantic, Markdown, python-dotenv, gunicorn
├── requirements-dev.txt            pytest, ruff, pdfplumber (content extraction tooling only)
├── pyproject.toml                  [tool.ruff] · [tool.pytest.ini_options] · [tool.vercel] entrypoint
├── .python-version                 3.12
├── .gitignore · .vercelignore · .env.example · Dockerfile
├── README.md                       rewritten in Phase 10 (stack, setup, how to add a project)
├── 00_MASTER_BUILD.md … 10_*.md, SETTING.md   build specs; move to docs/build/ in Phase 10
│
├── app/                            Python package
│   ├── __init__.py                 create_app(config_name): config, content registry, blueprints,
│   │                               error handlers, context processors, template filters, security headers
│   ├── routes/
│   │   ├── pages.py                GET /  /skills  /timeline  /contact
│   │   ├── projects.py             GET /projects  /projects/<slug>  (+ HTMX filter partial)
│   │   └── search.py               GET /search  (+ HTMX results partial)
│   ├── services/
│   │   ├── project_service.py      catalog access, filtering by category/technology/service, ordering
│   │   ├── search_service.py       in-memory index and ranked query
│   │   ├── relation_service.py     technology → cases graph, related-case scoring
│   │   ├── diagram_service.py      deterministic columnar layout for architecture nodes/edges
│   │   └── seo_service.py          title/description/OG/canonical per page and per project
│   ├── models/                     pydantic models (see sketch above)
│   ├── content/
│   │   ├── loader.py               discover content/, parse YAML + Markdown, validate, build registry
│   │   ├── registry.py             immutable ContentRegistry + derived indices
│   │   ├── markdown.py             Markdown → HTML with a fixed extension set
│   │   └── errors.py               ContentError with file path and field location
│   └── utils/                      slugify, dates, htmx request detection, static_url cache-buster
│
├── templates/
│   ├── base.html                   <head> meta/OG/canonical, skip link, nav, app shell, footer, scripts
│   ├── pages/                      home.html · skills.html · timeline.html · contact.html · search.html
│   ├── projects/
│   │   ├── index.html              case board / filter view
│   │   ├── detail.html             THE reusable case renderer: iterates the section list
│   │   └── sections/               case_header · the_case · evidence · architecture · breakdown ·
│   │                               findings · challenges_solutions · result · stack · links · related
│   ├── components/                 Jinja macros: case_file, evidence_card, evidence_tag, status_indicator,
│   │                               tech_badge, metric_card, timeline_node, terminal_panel, technical_note,
│   │                               architecture_diagram, modal, drawer, tooltip, command_palette, nav
│   ├── partials/                   HTMX fragments: search_results · project_grid · node_detail
│   └── errors/                     404.html · 500.html (case-file styled)
│
├── static/
│   ├── css/                        tokens.css · base.css · components.css · room.css · case.css
│   ├── js/                         vendor/htmx.min.js (pinned) · room.js · diagram.js · palette.js
│   ├── images/                     profile/ · projects/<slug>/   (WebP; size and alt declared in YAML)
│   ├── icons/                      sprite.svg (inlined through a Jinja include)
│   └── diagrams/                   optional static exports only; live diagrams are generated
│
├── content/
│   ├── taxonomy.yaml               categories, technology groups and aliases, AWS service labels
│   ├── projects/<slug>/
│   │   ├── project.yaml            metadata, stack, evidence, architecture, links, timeline
│   │   └── case.md                 narrative: the case, findings, breakdown sections
│   ├── profile/                    profile.yaml · intro.md
│   ├── skills/skills.yaml
│   └── timeline/timeline.yaml
│
├── tests/                          conftest.py · test_content.py · test_routes.py · test_search.py ·
│                                   test_relations.py · test_diagram.py · test_extensibility.py
│
└── docs/
    ├── ARCHITECTURE.md             this file
    ├── CONTENT_GUIDE.md            Phase 02: schema, how to add a project, diagram, images
    └── sources/                    the four PDFs — ignored by git, README.md explains why
```

Why the deviations from the suggested tree:

- `wsgi.py` instead of `app.py`: avoids the module/package shadowing described in the debt list and is
  the name both `flask run` and gunicorn recognise.
- `pyproject.toml` is added next to `requirements.txt`: dependencies stay in requirements files (the
  sibling-project convention and what Vercel installs from), while tool configuration and the Vercel
  entry point live in one place.
- `templates/projects/sections/` is added so the case renderer is a list of includes rather than one
  long template, and a new section is one new file.

---

## Request flow

```text
Browser
  │  GET /projects/technodev-devops-cicd           (optionally with header HX-Request: true)
  ▼
Vercel Python function  (or gunicorn / flask run)
  ▼
wsgi.py → app = create_app()              content registry already loaded at process start
  ▼
routes/projects.py :: detail(slug)
  │   registry.get_project(slug)  → None → abort(404)  → errors/404.html (case-file style)
  ▼
services
  │   project_service.sections_for(project)   → ordered list of sections that have content
  │   relation_service.related(project)       → related cases, shared technologies
  │   diagram_service.layout(project.architecture) → positioned nodes/edges for inline SVG
  │   seo_service.for_project(project)        → title, description, OG image, canonical
  ▼
render_template("projects/detail.html", …)   or   "partials/…"  when HX-Request is present
  ▼
HTML response + security headers (after_request)
```

### Routes

| Method + path | Blueprint | Full page | HTMX partial |
|---|---|---|---|
| `GET /` | pages | home: case room | — |
| `GET /projects` | projects | case board with filters (`?category=&tech=&service=&status=`) | `partials/project_grid.html` |
| `GET /projects/<slug>` | projects | case file | `partials/node_detail.html` for `?node=<id>` |
| `GET /skills` | pages | skills grouped by domain, each skill links to cases | — |
| `GET /timeline` | pages | merged timeline of all cases | — |
| `GET /contact` | pages | contact links (no form, no secrets) | — |
| `GET /search` | search | results page (`?q=`) | `partials/search_results.html` |
| `GET /healthz` | pages | JSON `{"status": "ok", "cases": n}` for deployment checks | — |

Error handling: 404 and 500 render case-file styled pages. An unknown project slug is a normal 404.
A content validation error at startup is fatal and prints the offending file and field, so a broken
content file never reaches production silently.

HTMX negotiation: a route checks `request.headers.get("HX-Request")` through a small helper and picks the
partial template; query parameters are identical for both forms, so URLs stay shareable and the feature
works without JavaScript.

---

## Content flow

```text
content/
  taxonomy.yaml ─────────────┐
  projects/<slug>/project.yaml ──► loader.py ──► pydantic models ──► ContentRegistry ──► app.extensions["content"]
  projects/<slug>/case.md ───┘      │                │                    │
  profile/*, skills/*, timeline/*   │                │                    ├── projects (ordered by case_number)
                                    │                │                    ├── by_slug, by_id
                                    │                │                    ├── technologies → cases
                                    │                │                    ├── aws_services → cases
                                    │                │                    ├── search index (tokens → documents)
                                    │                │                    └── related-case scores
                                    │                └── ContentError(file, field, message) on failure
                                    └── Markdown → HTML (fixed extension set, no raw HTML passthrough)
```

Loader steps:

1. Discover `content/projects/*/project.yaml`. Each directory is one case; the directory name must equal
   `slug`.
2. `yaml.safe_load`; merge `case.md` as `body_html`, and optional `*.md` files named after breakdown
   sections (`infrastructure.md`, `security.md`, …) into `breakdown`.
3. Validate with pydantic. Additional cross-file checks: unique `id`, `slug`, `case_number`; every
   technology and service is known to `taxonomy.yaml` (or is added to a warning list); every `evidence.src`
   exists under `static/`; every architecture edge references existing node ids; `related` entries are
   real slugs.
4. Build derived indices once. Relationships are derived from shared technologies and services, weighted
   by taxonomy group, so "AWS appears in four cases" and "Kubernetes appears in IaaS" are computed, not
   typed.
5. Freeze the registry and attach it to the app.

Reload policy: `DevelopmentConfig` re-checks content file mtimes on each request and rebuilds the
registry when something changed, so editing content is live. `ProductionConfig` loads once per process.

Link-state rule (from `SETTING.md`): templates call one macro, `link_or_state(link, label)`. It renders an
anchor only when `status == "public"` and `url` is set; otherwise it renders the state label. No template
constructs a GitHub URL by hand.

Honesty rule: `results` and `highlights` hold only statements supported by the source material or the
code. Targets from a brief (for example RTO/RPO) are stored under a `targets` key and rendered with the
label "target from module specification". Anything not supported is omitted or labelled `Not documented`.

---

## Template flow

```text
base.html
├── block meta        ← seo_service output (title, description, OG, canonical)
├── nav               ← components/nav macro (same on every page, keyboard reachable)
├── block content
│   ├── pages/home.html          investigator dossier · investigation board · system monitor · terminal panel
│   ├── projects/index.html      filters + components/case_file cards (HTMX swaps partials/project_grid)
│   ├── projects/detail.html     for section in sections: include "projects/sections/" ~ section ~ ".html"
│   ├── pages/skills.html · timeline.html · contact.html · search.html
│   └── errors/404.html · 500.html
├── footer
└── block scripts     ← htmx + the modules a page actually needs
```

Rules:

- Macros in `templates/components/` are the only place a UI pattern is defined. Pages import them;
  they never re-implement a card or badge inline.
- `projects/detail.html` receives `sections`, an ordered list computed by `project_service.sections_for`,
  containing only sections with content. Adding a section means adding one file under
  `projects/sections/` and one entry in the section order list.
- `partials/` templates are included by the full pages and returned directly for HTMX requests, so a
  fragment has exactly one source.
- Templates use token classes and component classes only. Raw colour values, pixel magic numbers, and
  inline styles are not allowed; a test greps for them.
- Every interactive element is a real `<a>` or `<button>`; hover effects always have a focus and
  touch equivalent.

---

## Asset strategy

### CSS

- `tokens.css` defines every custom property required by Phase 03 (background, surface,
  surface-elevated, border, text-primary/secondary/muted, accent-active (amber), accent-success (green),
  accent-warning, accent-danger (red), shadow, radius, spacing scale, type scale, motion durations).
- `base.css` (reset, typography, layout primitives), `components.css` (one block per macro),
  `room.css` (home composition and its breakpoints), `case.css` (case renderer and diagram).
- Linked from `base.html` with a cache-busting query string derived from file mtime by a `static_url`
  helper. No bundler, no preprocessor.
- `prefers-reduced-motion` disables all non-essential animation in one media block.

### JavaScript

Policy: the page must be complete without it. Three modules, each under a few hundred lines, loaded with
`defer`:

| Module | Purpose | Without it |
|---|---|---|
| `vendor/htmx.min.js` | partial swaps for filters, search, node detail | links and forms perform full page loads to the same URLs |
| `room.js` | hover/focus highlighting of related cases and technologies on the board | cards are plain links |
| `diagram.js` | node focus, dimming unrelated nodes, keyboard navigation inside the SVG | static SVG with `<title>` tooltips remains readable |
| `palette.js` | `Ctrl+K` command palette over the same search endpoint | nav and `/search` page |

HTMX is vendored and version-pinned so development works offline and the Content-Security-Policy can stay
`script-src 'self'`.

### Images and icons

- Project images live in `static/images/projects/<slug>/`, WebP preferred, with `width`, `height`, and
  `alt` declared in the evidence entry so templates can reserve layout space and lazy-load.
- One inline SVG sprite in `static/icons/sprite.svg`, included by Jinja once per page and referenced
  with `<use>`.
- Open Graph image: one default per site plus an optional per-project image referenced from YAML.

### Architecture diagrams

Diagrams are data (`architecture.groups/nodes/edges`) rendered to inline SVG by a Jinja macro using
positions computed by `diagram_service`:

1. Nodes are assigned to columns by their group order (for example Source → Pipeline → Compute → Data →
   Delivery), or by longest-path depth when groups are absent.
2. Within a column, nodes are stacked in declaration order with fixed spacing.
3. Edges are drawn as orthogonal or cubic paths between node anchors with an arrow marker and optional
   label; `direction: both` draws two markers.
4. The SVG uses a `viewBox` and scales with its container; on narrow screens it sits inside a
   horizontally scrollable region.
5. Each node carries `<title>` and `<desc>` so the static SVG is readable and accessible; `diagram.js`
   adds focus and dimming.

No per-project hand-drawn SVG. A PNG export of the original module figure can additionally appear as
evidence where it exists.

### Fonts

System UI stack by default. If a branded pair is chosen in Phase 03, at most two self-hosted WOFF2 files
(one sans-serif, one monospace), preloaded, with `font-display: swap`.

### Node.js policy

The user has permitted Node.js when genuinely needed. The baseline needs none. If a later phase adds
minification or image conversion, it enters as optional developer tooling with a documented script, and
the site must still build and run with Python alone. Node is never part of rendering or routing.

---

## Testing strategy

| Suite | What it proves |
|---|---|
| `test_content.py` | every content file loads and validates; ids, slugs, and case numbers are unique; link states are valid; every evidence `src` exists; unknown technologies are reported; Markdown renders |
| `test_routes.py` | every core route returns 200; every project slug returns 200; unknown slug returns the 404 case page; the 500 handler renders; `/healthz` reports the case count |
| `test_search.py` | title, technology, AWS service, category, and architecture node labels are searchable; empty and no-result states render |
| `test_relations.py` | technology → cases index is derived correctly; related cases exclude self and are ordered by score |
| `test_diagram.py` | every edge references existing nodes; layout is deterministic; SVG contains every node label |
| `test_htmx.py` | a request with `HX-Request` returns a fragment without the base layout; the same URL without the header returns a full page |
| `test_extensibility.py` | a temporary project directory created in `tmp_path` renders through the unchanged renderer; removing it removes the page |
| template lint (in `test_templates.py`) | no raw hex colours or inline styles in templates; every `<img>` has `alt` |

Tooling and commands (run from the repo root with the 3.12 environment):

```text
uv venv --python 3.12 && uv pip install -r requirements.txt -r requirements-dev.txt
py -3.12 -m pytest
py -3.12 -m ruff check . && py -3.12 -m ruff format --check .
py -3.12 -m compileall -q app config.py wsgi.py
```

A GitHub Actions workflow (Python only, GitHub-hosted runner) runs the same commands on push and pull
request. Each phase ends with the suite green before the next phase begins.

---

## Deployment strategy

### Target: Vercel Python runtime

- Detection is zero-config: Vercel reads `requirements.txt`, recognises Flask, and loads the entry point
  declared in `pyproject.toml`:

  ```toml
  [tool.vercel]
  entrypoint = "wsgi:app"
  ```

- No `vercel.json` rewrite to an `api/index.py` handler. A sibling project recorded that this pattern
  rewrites the path the application receives and every route 404s.
- `.vercelignore` excludes `tests/`, `docs/`, `.venv/`, `*.md` specs, and anything else not needed at
  runtime.
- Configuration comes only from environment variables: `APP_ENV` (`production`), `SECRET_KEY`,
  `SITE_URL` (canonical and Open Graph URLs). There is no database and no filesystem writes, so the
  serverless model fits: content is loaded once per cold start (a few hundred kilobytes of YAML and
  Markdown).
- Static assets: `static/` remains canonical. Phase 10 validates, with a preview deployment, whether
  they are served from Vercel's CDN (a copy into `public/` during build) or through the function with
  long `Cache-Control` headers. Both keep the repository layout unchanged.

### Portable alternative

A `Dockerfile` (python:3.12-slim, gunicorn, non-root user, `HEALTHCHECK` on `/healthz`) allows the same
code to run on any container host or VPS. On Windows, `waitress-serve wsgi:app` gives a production-like
local run.

### Configuration classes

| Class | DEBUG | Content reload | Security headers | Notes |
|---|---|---|---|---|
| `DevelopmentConfig` | on | on mtime change | relaxed CSP for the debugger | `flask --app wsgi run` |
| `TestingConfig` | off | per test app | on | `CONTENT_DIR` can point to a temp directory |
| `ProductionConfig` | off | load once | strict | requires `SECRET_KEY` and `SITE_URL` |

Security headers set in `after_request`: `Content-Security-Policy` (`default-src 'self'`; inline SVG
and data: images allowed), `X-Content-Type-Options: nosniff`, `Referrer-Policy:
strict-origin-when-cross-origin`, `Permissions-Policy` minimal. External links render with
`rel="noopener noreferrer"`.

### Repository and identity

- Remote: `https://github.com/Sann2267/portfolio` (public).
- The machine's global git identity belongs to a different account, so this repository sets
  `user.name`, `user.email`, and a `gh`-based credential helper locally. Commits and pushes must show
  `Sann2267 <ibnuadzim2@gmail.com>`.
- `docs/sources/` (the competition PDFs) is ignored; only derived content is committed.
- No secrets in content or templates. Values found in source repositories' configuration files are
  never copied into the portfolio.

---

## Extensibility strategy

| Change | What is touched | What is not touched |
|---|---|---|
| Add a project | `content/projects/<slug>/project.yaml`, `case.md`, images under `static/images/projects/<slug>/` | any Python or template file |
| Add a technology or category | `content/taxonomy.yaml` | filters and badges pick it up automatically |
| Add an architecture diagram | the `architecture` block of the project's YAML | `diagram_service`, the SVG macro |
| Add a case section | one optional model field, one file in `templates/projects/sections/`, one entry in the section order list | other sections, other pages |
| Add a page | one route function and one template | content layer |
| Change the visual language | `tokens.css` | component markup |

Invariants guarded by tests: the renderer is unchanged when a fake project is added
(`test_extensibility.py`); every link state renders without a broken anchor; every section renders only
with content. `docs/CONTENT_GUIDE.md` (written in Phase 02, completed in Phase 10) documents the schema
with a copy-paste template for a new case.

---

## Risks and trade-offs

| Risk or trade-off | Impact | Mitigation |
|---|---|---|
| The source PDFs are competition briefs describing *required* outcomes, not verification reports | Results sections could overstate what was achieved | `results` hold only what the brief plus the author's code support; wording "implemented per module requirements"; the user supplies screenshots where available |
| Fictional scenario companies (TechnoDev, NusaCommerce) | Could read as client work | `context` field states the competition origin on every such case |
| IoT module PDF is image-only | Content cannot be extracted by text tools | Rasterize pages with pdfplumber/pypdfium2, transcribe visually, label unclear items `Not documented` |
| IoT implementation differs from the phase 02 outline (EC2 + Mosquitto vs IoT Core + X.509/TLS) | Risk of claiming security features that were not implemented | Nodes carry `status: implemented / planned`; the diagram renders planned nodes visibly differently |
| Case 004 application code was provided as competition assets | Risk of claiming authorship of provided code | Role field: infrastructure, orchestration, and integration; breakdown names what was provided |
| Cases 001/002 facts must come from local code | Memory-based claims could be wrong | Phase 02 reads the README files and code before writing content |
| `python` on PATH is 3.10 | Accidental wrong interpreter | `.python-version`, uv-created venv, documented commands use `py -3.12` |
| Global git identity is the wrong account | Commits attributed to a different person | Per-repo identity and credential helper; verified on the first commit |
| Vercel serverless cold starts | First request re-parses content | Content is small; registry build is measured in tests; Dockerfile is the fallback |
| Static asset serving on Vercel unvalidated | Assets could be served through the function | Validated in Phase 10 with a preview deployment; both options keep the layout |
| Keeping spec files at the repo root | Public repo shows build prompts | Relocated to `docs/build/` in Phase 10 |
| No database | No admin UI for content | Intentional: content is versioned in git and reviewed like code |
| Plain CSS, no preprocessor | Some repetition | Tokens and component classes keep it manageable; Node tooling allowed later if needed |

---

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Flask application factory, `wsgi.py` entry point, `app/` package | Spec requirement; avoids module/package shadowing |
| 2026-09-09 | YAML + Markdown content validated by pydantic v2 | Spec preference; sibling-project convention |
| 2026-09-09 | No database, no forms library, contact page is links | No persistent data; avoids secrets and spam handling |
| 2026-09-09 | HTMX vendored and pinned; three small vanilla JS modules | Progressive enhancement, strict CSP |
| 2026-09-09 | Server-rendered SVG diagrams from data with Python layout | Spec requires readability without JavaScript |
| 2026-09-09 | Deployment on Vercel Python runtime; Dockerfile kept | User's existing platform; portability |
| 2026-09-09 | Public repository `Sann2267/portfolio`; old `Sann2267/portofolio` archived | User decision |
| 2026-09-09 | Source PDFs kept out of git under `docs/sources/` | Competition material is not for publication |
| 2026-09-09 | Node.js allowed as optional dev tooling only | User permission; Python-only baseline preserved |
| 2026-09-09 | IoT case sourced from the presentation deck plus the author's statement; the similarly named public repository is an AI-generated reconstruction and is not linked | User clarification |
| 2026-09-09 | Claims carry a `basis`; `future_work` must be `planned`; competition-provided components are described as provided | Honesty rules from the master build |
| 2026-09-09 | `case.md` is split on `## ` headings into a fixed set of sections; unknown headings are errors | Keeps the single case renderer deterministic |
| 2026-09-09 | Skills list taxonomy names only; cases per skill are derived by the registry and a skill without a case fails the tests | Evidence-based skills page, no self-rated levels |
| 2026-09-09 | Cases 003 and 004 credit infrastructure and orchestration work; workflow definitions, Lambda code, ETL scripts, and dashboards were provided by the modules | Module text states the assets were provided |

---

## Phase status and handoff

Phase 02 (content model) delivered `app/models`, `app/content` (loader, registry, Markdown, CLI
validator), `content/` for all six cases plus profile, skills, timeline, and taxonomy, the test suite
under `tests/`, and `docs/CONTENT_GUIDE.md`. All PDF and repository sources were read; the schema was
frozen from the union of `00`, `02`, `06`, `07`, and `SETTING.md`.

Open items carried into later phases:

1. No screenshot or image evidence exists yet. Evidence lists documentation, architecture, and
   technical breakdown only; `static/images/projects/<slug>/` is empty until the user supplies assets.
2. The deck's dashboard image for case 006 is a stock Node-RED image and must not be used as a
   screenshot.
3. Phase 03 defines the visual tokens; Phase 04 wires `load_registry` into the Flask factory with the
   dev-mode reload described under Content flow; Phase 07 implements the layout for the
   `architecture` data already present in every case.
