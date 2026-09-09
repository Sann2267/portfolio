# PHASE 10 — VERIFICATION AND RELEASE

## OBJECTIVE

Verify the portfolio before release.

## PYTHON CHECKS

Run appropriate checks for the repository, including when available:

- Python syntax validation
- import validation
- pytest
- linting
- formatting check
- Flask route validation
- production configuration validation

## APPLICATION CHECKLIST

Verify:

- homepage
- projects index
- every project detail page
- search
- filters
- skills
- timeline
- contact
- 404
- 500

## VISUAL CHECKLIST

Verify:

- no broken images
- no layout overflow
- no accidental scrollbars
- no unreadable text
- no broken architecture diagrams
- no excessive animation
- no inconsistent components

## CONTENT CHECKLIST

Verify factual claims against the supplied project documents.

Never invent:

- metrics
- uptime
- traffic
- performance
- ML accuracy
- production clients
- revenue
- certifications

Mark unsupported information as:

- not documented
- planned
- future work

## SECURITY CHECKLIST

Verify:

- no secrets committed
- no credentials in content
- no tokens in templates
- safe external links
- safe URL handling
- secure production configuration

## FINAL UX TEST

A new visitor should understand the following within a few seconds:

1. who the developer is,
2. what fields they work in,
3. where the projects are,
4. how to open a case,
5. what technologies are demonstrated.

## EXTENSIBILITY TEST

Create a temporary fake project entry in the content layer.

Confirm that the website can render it without modifying the core project page template.

Remove the temporary project after the test.

## RELEASE OUTPUT

Update:

- README.md
- docs/ARCHITECTURE.md
- docs/CONTENT_GUIDE.md

README must explain:

- stack
- local setup
- project structure
- how to add a project
- how to add an architecture diagram
- how to add images
- how to run tests
- how to run in production

## EXIT CRITERIA

The project passes verification and is ready for deployment.
