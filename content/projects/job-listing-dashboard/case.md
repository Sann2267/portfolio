## The Case

The scraping pipeline (case 001) produces a growing corpus of job posts as JSON, CSV, and
SQLite on one machine. Reading it meant opening files. The goal was a dashboard that lets a
user browse, filter, and save vacancies, lets an admin start and watch scraper runs from a
browser, and can be deployed on a platform that has no access to that machine.

```text
SCRAPING  ->  PROCESSING  ->  API  ->  DASHBOARD  ->  USER
(case 001)    (worker sync)   (FastAPI on Vercel)   (React)
```

## Key Findings

- **Separate what runs where.** The deployed API can never execute the scraper, so it only
  queues work. A worker on the machine with the tools claims jobs, runs them as subprocesses
  exactly as their Makefiles do, and writes progress into the shared database. This is what lets
  a Vercel deployment start and watch a scrape it could not run itself.
- **The corpus is somebody else's.** The scraper owns `job_posts` and `runs`. The app opens the
  SQLite file read-only at the driver level and keeps a Postgres copy for the deployed API,
  refreshed incrementally with a 24-hour overlap.
- **One filter object drives the page.** The job list, the statistics, and the analytics share
  one filter definition, so the numbers in every chart always describe the rows in the list.
- **AI is optional and bounded.** Everything the model produces is stored in the app database,
  never in the corpus. Quotas are per user per day because the provider's free tier is per
  organisation.

## Application

FastAPI with SQLAlchemy 2.0, JWT authentication (PyJWT, bcrypt), roles `admin` and `user`.
Endpoint groups: auth, jobs, stats, analytics, meta, runs, saved, ops, admin, and ai.

The worker claims queued rows with a conditional UPDATE, heartbeats every ten seconds, marks
its own rows aborted if it died mid-job, exits between jobs when the backend code changed, and
is kept alive by a scheduled task with a restart supervisor.

The frontend is a Vite + React 19 single-page app with Recharts, hand-written CSS with design
tokens, dark mode as a token swap, and a table twin for every chart.

## Data

Two databases addressed by URL: the read-only corpus (SQLite locally, Postgres copy when
deployed) and the app store (users, saved jobs, operations queue, log lines, worker heartbeats,
AI notes and enrichment). The migration script upserts and is safe to re-run; the worker syncs
new and changed rows after every scrape and on demand.

Flyer images come from the scraper's local cache, an S3-compatible bucket the worker fills, or
the Instagram CDN URL as a last resort, in that order.

## Deployment

Two Vercel projects from one repository. The backend is zero-config Python: Vercel detects the
FastAPI app from `requirements.txt` and loads the entry module, no rewrite rules. The frontend
is a static build with every path rewritten to `index.html`. Long-running work stays on the
worker because functions are capped at 300 seconds.

## Result

A working dashboard with a queue-driven operations page, a Postgres-backed deployment, and AI
features that degrade to "not configured" rather than failing. Tests run against a mock AI
provider without any key. Usage numbers and uptime are not tracked.
