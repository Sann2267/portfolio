# Case Room — a Python-first detective-room portfolio

A personal technical portfolio built as an investigation room: every project is a **case
file**, every architecture is **evidence**, every technical decision is part of the
investigation. The cases cover cloud infrastructure, DevOps, backend, data engineering, and IoT
on AWS.

The whole site is data-driven. Adding a case means adding a YAML file and a Markdown file;
no template changes. Every statement carries a basis (documented, verified in code,
implemented but undocumented, target from a specification, planned, not documented) and the
UI shows it.

| | |
|---|---|
| Stack | Python 3.12 · Flask 3 · Jinja2 · pydantic v2 · PyYAML · Markdown · HTMX 2 (vendored) · plain CSS · five small vanilla JS modules |
| No | TypeScript, React, Next.js, Node build steps, databases, webfonts, trackers |
| Source | https://github.com/Sann2267/portfolio |
| Docs | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/CONTENT_GUIDE.md](docs/CONTENT_GUIDE.md) · [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) |

---

## 1. Local setup

Requirements: Python 3.12 (on this machine only `py -3.12` is 3.12; `python` on PATH is 3.10)
and optionally [uv](https://docs.astral.sh/uv/).

```powershell
# Windows (PowerShell)
uv venv --python 3.12 .venv            # or: py -3.12 -m venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt
.venv\Scripts\python -m flask --app wsgi run --port 5000
```

```bash
# macOS / Linux
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi run --port 5000
```

Open http://127.0.0.1:5000. In development (`APP_ENV` unset or `development`) the content
directory is re-read whenever a file changes, so editing a case is live.

Environment variables (see `.env.example`):

| Variable | Purpose | Default |
|---|---|---|
| `APP_ENV` | `development`, `testing`, or `production` | `development` |
| `SECRET_KEY` | Flask secret; required in production | development-only value |
| `SITE_URL` | Canonical and Open Graph URLs, sitemap; falls back to Vercel's hostname or the first request's host, with a warning | `http://127.0.0.1:5000` |
| `CONTENT_DIR` | Alternative content directory | `./content` |

---

## 2. Project structure

```text
wsgi.py                    entry point: app = create_app()   (Flask, gunicorn, Vercel)
config.py                  Development / Testing / Production configuration
app/
  __init__.py              application factory, context processors, error pages, security headers
  routes/                  pages.py (room, skills, timeline, contact, sitemap, robots, health)
                           projects.py (case index, case renderer, node details, technology pages)
                           search.py (full page and fragments for htmx and the command palette)
  services/                project_service (filters, sections), search_service (index),
                           relation_service (related cases, technology views),
                           diagram_service (deterministic SVG layout), seo_service (metadata),
                           scene_service (home-page cutscene script and clickable objects)
  models/                  pydantic content models (Project, Architecture, Profile, Skills, Taxonomy…)
  content/                 loader, registry, Markdown rendering, `python -m app.content` validator
templates/
  base.html · pages/ · projects/ (index, detail, sections/) · components/ (macros) · partials/ · errors/
  partials/scene.svg       the illustrated case room (inline SVG, coloured only through CSS classes)
static/
  css/ (tokens, base, components, room, case, scene) · js/ (app, room, scene, audio, diagram, palette, vendor/htmx)
  images/ · icons/
content/
  taxonomy.yaml · profile/ · skills/ · timeline/ · projects/<slug>/project.yaml + case.md
tests/                     content, models, routes, room, case system, diagram, navigation,
                           accessibility, SEO, release checks
docs/                      ARCHITECTURE.md · CONTENT_GUIDE.md · DESIGN_SYSTEM.md · build/ (phase specs)
```

Request flow: route → service → content registry (loaded once, validated with pydantic) →
Jinja template. The same route returns a full page or an HTML fragment when htmx asks.

**Home page intro.** The room opens on an illustrated case room with a short, skippable cutscene
(Skip button, Esc, or Enter) and clickable objects: the filing cabinet leads to Skills, the hat to
the dossier, the corkboard to the investigation board, the telephone to Contact, the case folder
to the case files, the magnifying glass to search, the typewriter to the timeline, the lamp shows
every object's label, the monitor jumps to the system status. The intro plays once per browser
tab (`sessionStorage["caseroom.introSeen"]`), never under `prefers-reduced-motion`, and can be
replayed. Sound effects are synthesised in the browser, off by default, and remembered in
`localStorage["caseroom.sound"]`. The narration lines live in `content/profile/profile.yaml`
(`cutscene`). Without JavaScript the room renders lit and every object is a plain link.

---

## 3. Adding a case

1. Create `content/projects/<slug>/project.yaml` and `content/projects/<slug>/case.md`.
   Copy an existing case as a starting point; the full schema is in
   [docs/CONTENT_GUIDE.md](docs/CONTENT_GUIDE.md).
2. Use the next `case_number` and the matching `id` (`case-007`).
3. Use technology names from `content/taxonomy.yaml`; add new ones there first.
4. Validate: `.venv\Scripts\python -m app.content` (prints every case and any error with the
   file and field).
5. Run the tests. The renderer, the board, search, filters, the sitemap, and the command
   palette pick the case up automatically.

Sections in `case.md` are `## The Case`, `## Key Findings`, the technical breakdown headings
(`## Infrastructure`, `## Application`, `## Data`, `## Security`, `## Networking`,
`## Observability`, `## Deployment`), `## Result`, and `## Notes`. Only the headings you write
are rendered.

Link states (`repository`, `demo`, `documentation`) are `public | private | archived |
deleted | unavailable`; a link renders only when public, otherwise the state and a note.

---

## 4. Adding an architecture diagram

Diagrams are data in `project.yaml`:

```yaml
architecture:
  groups:
    - {id: device, label: Device}
    - {id: cloud, label: AWS}
  nodes:
    - {id: esp32, label: ESP32, service: ESP32, group: device, description: "Reads the sensor."}
    - {id: iot_core, label: AWS IoT Core, service: AWS IoT Core, group: cloud}
    - {id: telegram, label: Telegram alerts, service: Telegram Bot API, group: future, status: planned}
  edges:
    - {source: esp32, target: iot_core, label: MQTT publish, protocol: "MQTT over TLS, X.509"}
```

Groups become columns (wrapping after four), nodes stack inside their group, edges are drawn
between them. Node `status` (`implemented`, `planned`, `provided`, `external`,
`not_documented`) changes the outline. Hover or focus traces connections; selecting a node
loads its details from `/projects/<slug>/nodes/<id>`. A text version is always rendered.

---

## 5. Adding images

Put files under `static/images/projects/<slug>/` (WebP preferred) and reference them from the
case's `evidence` or `gallery` list with `alt`, `width`, and `height`:

```yaml
evidence:
  - {kind: screenshot, title: "CloudWatch dashboard", src: images/projects/x/dashboard.webp,
     alt: "Dashboard with Lambda invocations and errors", width: 1600, height: 900}
```

The loader fails if the file is missing. Images are lazy-loaded and served with a
cache-busting version query derived from a content hash.

---

## 6. Tests and checks

```powershell
.venv\Scripts\python -m pytest                     # about 150 tests, no network
.venv\Scripts\python -m ruff check . ; .venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m compileall -q app config.py wsgi.py
.venv\Scripts\python -m app.content                # content validation with a summary
.venv\Scripts\python -m flask --app wsgi routes    # route table
```

What the tests cover: content validation and honesty rules, models, every route and error
page, htmx fragments, the room composition, the single case renderer (sections omitted when
empty, cross-links), the diagram layout, search and filters, the command palette markup,
accessibility structure of every page (one `h1`, labelled controls, named links and buttons,
skip link, alt text), SEO metadata, sitemap and robots, the asset budget, production
configuration, a secret scan, the case-room scene (nine hotspots with real targets, narration
that obeys the honesty rules, a decorative drawing coloured only through classes, scripts that
load no media), and an end-to-end fake-project test that adds a seventh case in a temporary
directory and renders it without touching any template.

GitHub Actions runs the same checks on every push (`.github/workflows/ci.yml`).

Visual checks during the build used a headless Edge sweep of every route at desktop, tablet,
and mobile widths (no horizontal overflow, keyboard focus order, reduced motion). That tool
lives outside the repository because it needs Node.

---

## 7. Running in production

Set `APP_ENV=production` and `SECRET_KEY`; the app refuses to start in production without a
secret. Set `SITE_URL` to the public origin. If it is missing, the app uses Vercel's
`VERCEL_PROJECT_PRODUCTION_URL` when present, otherwise the host of the first request, and
logs a warning.

**Vercel (Python runtime).** Zero configuration: Vercel installs `requirements.txt`, detects
Flask, and uses the entry point declared in `pyproject.toml` (`[tool.vercel] entrypoint =
"wsgi:app"`). Add the three environment variables in the project settings. `.vercelignore`
keeps tests and docs out of the deployment. Static files are served by the function; if you
want them on the CDN instead, copy `static/` to `public/static/` in a build step.

**Docker / any host.**

```bash
docker build -t case-room .
docker run --rm -p 8000:8000 -e SECRET_KEY=change-me -e SITE_URL=https://example.com case-room
```

The image runs gunicorn as a non-root user with a health check on `/healthz`. Behind a
reverse proxy, forward `Host` and `X-Forwarded-Proto` so canonical URLs use `SITE_URL`.

**Plain gunicorn.** `gunicorn -b 0.0.0.0:8000 -w 2 wsgi:app`.

---

## 8. Honesty rules

Nothing on the site claims a metric, uptime, accuracy value, client, or certification that the
source material does not support. Three cases come from LKS Nasional 2026 Cloud Computing
modules and say so; components that the module supplied are described as provided; results
that were not recorded are labelled `Not documented`; future work is always `Planned`. The
rules are enforced by tests and documented in [docs/CONTENT_GUIDE.md](docs/CONTENT_GUIDE.md).
