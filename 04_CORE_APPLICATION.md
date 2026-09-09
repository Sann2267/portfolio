# PHASE 04 — CORE APPLICATION

## OBJECTIVE

Implement the Python web foundation.

## REQUIRED STACK

- Python 3.12+
- Flask
- Jinja2
- HTMX where useful
- Vanilla JavaScript only where necessary
- CSS

No TypeScript.

No React.

No Next.js.

## APPLICATION LAYERS

Recommended separation:

ROUTES
↓
SERVICES
↓
CONTENT LOADER / DOMAIN MODELS
↓
TEMPLATES

Static assets remain separate.

## CREATE

- application factory or clean Flask app setup
- configuration layer
- route modules
- content loader
- project service
- search service
- error handlers
- template base layout
- reusable template components

## ROUTES

Implement at minimum:

GET /
GET /projects
GET /projects/<slug>
GET /skills
GET /timeline
GET /contact
GET /search

Search may use HTMX partial rendering.

## ERROR HANDLING

Create proper 404 and 500 pages.

Project not found must produce a readable case-file-style error page.

## TEMPLATES

Create:

- base.html
- homepage
- project index
- project detail
- skills
- timeline
- contact
- error pages
- reusable partials/macros

## EXIT CRITERIA

The Flask application starts successfully, routes resolve, templates render, and project content is loaded from the content layer.
