# PHASE 03 — DESIGN SYSTEM

## OBJECTIVE

Create the reusable visual system before building complex pages.

## EXPERIENCE

Theme:

Modern Detective Investigation Room + Cloud Operations Center.

The interface should feel like a physical room translated into a web application.

Possible visual objects:

- case files
- investigation board
- evidence cards
- evidence pins
- monitor screens
- terminal
- desk surfaces
- technical diagrams
- sticky notes
- status lights
- timestamps
- labels

Use these as visual metaphors only.

## DESIGN PRINCIPLES

1. Technical content has priority.
2. Navigation remains obvious.
3. Visual effects never obscure information.
4. Every interaction has a reason.
5. Reusable components are preferred over page-specific hacks.

## TOKENS

Create CSS custom properties for:

- background
- surface
- surface-elevated
- border
- text-primary
- text-secondary
- text-muted
- accent-active
- accent-success
- accent-warning
- accent-danger
- shadow
- radius
- spacing
- typography scale
- transition speed

Do not scatter raw color values throughout templates.

## COMPONENTS

Create reusable components such as:

- AppShell
- Navigation
- CaseFile
- EvidenceCard
- EvidenceTag
- StatusIndicator
- InvestigationBoard
- TerminalPanel
- TechnicalNote
- MetricCard
- TimelineNode
- TechnologyBadge
- ArchitectureNode
- ArchitectureEdge
- Modal
- Drawer
- Tooltip
- CommandPalette

Use Jinja macros/includes/components where appropriate.

## MOTION

Use subtle:

- reveal
- slide
- fade
- line tracing
- terminal typing
- evidence highlight
- case opening

Support:

`prefers-reduced-motion`

When reduced motion is enabled, disable non-essential animation.

## EXIT CRITERIA

A consistent design system exists and can be reused by every page.
