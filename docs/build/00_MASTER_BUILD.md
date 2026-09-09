# MASTER BUILD — PYTHON-FIRST INTERACTIVE DETECTIVE PORTFOLIO

## ROLE

You are a senior Python web engineer, UI/UX designer, interaction designer, and software architect.

Build a premium personal technical portfolio using a Python-first web architecture.

The portfolio belongs to a developer focused on:

- Cloud Infrastructure
- DevOps
- Backend Development
- Data Engineering / Data Analytics
- IoT
- AWS
- Automation

The portfolio must NOT look like a generic developer portfolio.

The visual concept is a sophisticated modern detective investigation room combined with a cloud operations / engineering control room.

The central storytelling idea is:

> Every project is a case. Every architecture is evidence. Every technical decision is part of the investigation.

The detective concept is a storytelling and navigation layer, NOT a gimmick that hides technical information.

---

# NON-NEGOTIABLE TECHNOLOGY CONSTRAINTS

## Python-first

The application code must be Python-based.

DO NOT use TypeScript.

DO NOT build the application using Next.js, React, Vue, Nuxt, SvelteKit, or another TypeScript-first framework.

Preferred stack:

- Python 3.12+
- Flask
- Jinja2
- SQLAlchemy only when persistent data is actually needed
- WTForms only when forms require it
- HTMX for lightweight server-driven interactions where useful
- Vanilla JavaScript only when browser-side behavior cannot reasonably be handled with HTML, CSS, HTMX, or Python
- CSS with a maintainable design-token system

The frontend may contain HTML/CSS and minimal JavaScript because browsers require client-side execution, but the application architecture, routing, content modeling, rendering logic, and business logic must remain Python-first.

Do not introduce Node.js tooling unless absolutely required by an unavoidable dependency. Prefer a build that can run with Python tooling alone.

---

# ARCHITECTURAL PRINCIPLE

The most important requirement is maintainability.

CONTENT != UI

PROJECT DATA != PAGE IMPLEMENTATION

The UI must consume structured project data.

Adding a new project in the future should require adding a content file and optional assets, not rewriting the project page.

The project detail page must be a reusable renderer.

---

# STRICT EXECUTION ORDER

You MUST follow the phase files in this order:

1. `01_AUDIT_AND_ARCHITECTURE.md`
2. `02_CONTENT_MODEL.md`
3. `03_DESIGN_SYSTEM.md`
4. `04_CORE_APPLICATION.md`
5. `05_DETECTIVE_ROOM_UI.md`
6. `06_PROJECT_CASE_SYSTEM.md`
7. `07_INTERACTIVE_ARCHITECTURE.md`
8. `08_SEARCH_FILTER_AND_NAVIGATION.md`
9. `09_RESPONSIVE_ACCESSIBILITY_PERFORMANCE.md`
10. `10_VERIFICATION_AND_RELEASE.md`

Do not skip a phase.

Do not execute future phases early.

Do not mix unrelated implementation tasks.

At the end of every phase:

1. inspect the implementation,
2. run validation,
3. fix discovered issues,
4. document what was completed,
5. document known limitations,
6. stop before beginning the next phase.

---

# SOURCE OF TRUTH

Use these provided project documents as factual references:

- `Modul - DevOps Automation.pdf`
- `Modul - Cloud Ai, Data Analytics.pdf`
- `Modul - Infrastructure as Service.pdf`
- `Monitoring IoT ESP32 & AWS.pdf`

Do not invent project metrics, production usage, company/client relationships, traffic, performance numbers, accuracy values, uptime, certifications, or achievements that are not supported by source material.

When a detail is uncertain or unavailable, label it appropriately:

- `Not documented`
- `Implemented in project environment`
- `Planned`
- `Future improvement`

Never turn a planned feature into a completed feature.

---

# TARGET PORTFOLIO CASES

The portfolio must contain these major cases:

1. Indonesia Job Data Scraping System
2. Job Listing Fullstack Dashboard + API
3. TechnoDev DevOps CI/CD Platform
4. NusaCommerce Cloud AI / Data Analytics Platform
5. Multi-Tenant SaaS Infrastructure / IaaS
6. ESP32 + AWS IoT Monitoring

Treat these as case files inside one investigation system.

---

# DESIGN GOAL

The first impression should communicate:

"This is an engineer's investigation room containing real cloud, backend, data, and IoT evidence."

The design should be:

- dark
- elegant
- technical
- cinematic
- restrained
- highly readable
- premium
- interactive

Avoid:

- cartoon detective visuals
- childish illustrations
- excessive red strings
- unnecessary 3D effects
- fake hacking aesthetics
- excessive terminal decoration
- endless animations
- visual noise

---

# VISUAL LANGUAGE

Base colors:

- near-black
- charcoal
- graphite
- warm off-white

Semantic accents:

- amber = active investigation / highlighted evidence
- green = verified / operational
- red = warning / failed / security issue
- muted gray = metadata / inactive

Use accent colors sparingly.

Typography:

- clean sans-serif for primary content
- monospace for logs, commands, identifiers, technical labels, timestamps, system states

---

# MAIN EXPERIENCE

Conceptual environment:

CASE ROOM
├── investigator profile
├── investigation board
├── project evidence
├── system status
├── terminal / technical notes
├── timeline
└── contact / communication

The user must always understand how to navigate.

Interactivity must enhance exploration instead of becoming a puzzle that blocks content.

---

# PROJECT DETAIL EXPERIENCE

Every project opens as a reusable case file.

Recommended hierarchy:

CASE ID
TITLE
STATUS
CATEGORY
ROLE

THE CASE
What problem was being solved?

EVIDENCE
Screenshots / diagrams / logs / data flow

ARCHITECTURE
Interactive system diagram

IMPLEMENTATION
Infrastructure / backend / data / security / observability

KEY FINDINGS
Important engineering decisions

RESULT
What was achieved according to the source material?

STACK
Technologies and services

REPOSITORY / DEMO / DOCUMENTATION

---

# PYTHON-FIRST CONTENT ARCHITECTURE

Prefer:

`content/*.yaml` / `content/*.json` / `content/*.md`

or Python dictionaries/dataclasses loaded from external content files.

Project pages must be data-driven.

Recommended Python domain model:

```python
from dataclasses import dataclass, field
from typing import Literal

ProjectStatus = Literal["completed", "active", "experimental", "planned"]

@dataclass
class Project:
    id: str
    slug: str
    title: str
    category: str
    project_type: str
    status: ProjectStatus
    summary: str
    description: str
    technologies: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    architecture: dict = field(default_factory=dict)
    evidence: list[dict] = field(default_factory=list)
    repository: str | None = None
    demo: str | None = None
    documentation: str | None = None
```

The exact model may be improved during the architecture phase.

Do not copy this model blindly if a better design is found.

---

# REQUIRED CORE ROUTES

At minimum:

- `/`
- `/projects`
- `/projects/<slug>`
- `/skills`
- `/timeline`
- `/contact`
- `/search`

Additional routes may be added only when justified.

---

# REQUIRED FEATURES

- interactive landing room
- reusable project case pages
- project filtering
- global search
- technology/service filtering
- interactive architecture diagrams
- project relationships
- timeline
- evidence cards
- technical terminal / system notes
- responsive layout
- accessible keyboard navigation
- reduced motion support
- loading/error/empty states where relevant
- SEO metadata
- Open Graph metadata
- optimized assets

---

# PERFORMANCE RULES

Do not add heavy dependencies merely for effects.

Avoid:

- unnecessary WebGL
- large background videos
- complex 3D engines
- excessive client-side JavaScript
- enormous SVG blobs

Prefer:

- CSS transitions
- server-rendered HTML
- HTMX partial updates
- inline SVG only where useful
- lazy-loaded images
- efficient assets

---

# FINAL QUALITY STANDARD

The portfolio should feel like a serious technical artifact.

A recruiter should quickly understand:

1. who the developer is,
2. what kind of systems they build,
3. what technologies they use,
4. how their projects are architected,
5. what technical problems they solved,
6. how the projects relate to Cloud, DevOps, Backend, Data, and IoT.

A future project must be addable without redesigning the entire site.

Build a maintainable system, not just a visually impressive homepage.
