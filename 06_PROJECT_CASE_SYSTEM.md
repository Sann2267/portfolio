# PHASE 06 — PROJECT CASE SYSTEM

## OBJECTIVE

Create one reusable project detail renderer for all projects.

## REQUIRED PATTERN

`/projects/<slug>` loads a structured project and passes it into one reusable template.

Do not create six independently hardcoded project pages.

## CASE STRUCTURE

CASE HEADER

- Case ID
- Title
- Category
- Type
- Status
- Role if available

THE CASE

Problem / context / objective.

EVIDENCE

- screenshots
- diagrams
- logs
- code references
- architecture

ARCHITECTURE

Interactive nodes and connections.

TECHNICAL BREAKDOWN

Split into:

- infrastructure
- application
- data
- security
- networking
- observability
- deployment

Only render sections that have content.

KEY FINDINGS

Important engineering decisions.

CHALLENGES

Actual documented or clearly identified project challenges.

SOLUTIONS

Corresponding engineering approaches.

RESULT

Source-supported outcomes only.

STACK

Technology badges grouped logically.

LINKS

Repository / demo / docs only when present.

## CASE CROSS-LINKING

Show related cases.

Examples:

AWS appears in:

- DevOps
- Cloud AI
- IaaS
- IoT

Kubernetes appears in:

- IaaS

Python appears across multiple cases.

This relationship system must be data-driven.

## EXIT CRITERIA

All six projects use the same renderer while displaying different content and architecture.
