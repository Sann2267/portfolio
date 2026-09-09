# PHASE 01 — AUDIT AND ARCHITECTURE

## OBJECTIVE

Understand the repository before implementing anything.

## TASKS

1. Inspect all existing files.
2. Identify Python version.
3. Identify package manager and dependency system.
4. Identify framework.
5. Identify entry point.
6. Identify templates.
7. Identify styles.
8. Identify assets.
9. Identify test configuration.
10. Identify deployment configuration.
11. Identify existing content.
12. Identify technical debt or duplicated structures.

Do not delete existing work blindly.

## REQUIRED OUTPUT

Create:

`docs/ARCHITECTURE.md`

Include:

- current architecture
- proposed architecture
- folder structure
- request flow
- content flow
- template flow
- asset strategy
- testing strategy
- deployment strategy
- extensibility strategy
- risks and trade-offs

## TARGET STRUCTURE

Prefer a structure similar to:

```text
portfolio/
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── content/
│   └── utils/
│
├── templates/
│   ├── base.html
│   ├── pages/
│   ├── projects/
│   ├── components/
│   └── partials/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── icons/
│   └── diagrams/
│
├── content/
│   ├── projects/
│   ├── profile/
│   ├── skills/
│   └── timeline/
│
├── tests/
│
└── docs/
```

The exact structure may change if the repository already has a better convention.

## PYTHON REQUIREMENT

No TypeScript.

No React project.

No Next.js project.

Flask/Jinja must own application rendering.

Use HTMX or small vanilla JS only where needed for browser interaction.

## EXIT CRITERIA

The repository architecture is documented and ready for implementation.
