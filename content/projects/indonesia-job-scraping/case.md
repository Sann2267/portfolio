## The Case

Job vacancies in Indonesia are posted as Instagram flyers by hundreds of regional "loker"
accounts. The information a job seeker needs sits in an image caption and, more often, inside
the image itself. There is no API, no search for anonymous clients, and every account has its
own layout.

The task was to turn that stream into structured, de-duplicated records per province without
logging in, without bypassing any access control, and without inventing a single field.

## Key Findings

- **Reconnaissance before code.** A dedicated recon phase probed every public surface and
  recorded what Instagram refused. The design follows those results: account-based discovery,
  the public REST feed over GraphQL (whose `doc_id` rotates every few weeks), and TLS-fingerprint
  impersonation because Instagram gates on the fingerprint before it reads headers.
- **One module per stage.** A renamed field or a new pagination cursor touches one file. Every
  stage also has its own entry point, so a problem can be reproduced offline against captured
  data instead of re-hitting the network.
- **Schema as a contract.** The output model forbids unknown fields and a test asserts that no
  extractor ever fabricates a value. Raw OCR text is stored verbatim next to the parsed view.
- **A reader, not more regex.** Four thousand lines of patterns could not tell a heading from a
  field. The cleaning stage now asks a small model for structured JSON and then refuses any
  number, e-mail, title, or employer that does not survive validation against the source text.

## Data

Thirty-seven fields per post, defined once in a pydantic model. Contact information is
structured (e-mails, phones, raw phones, WhatsApp links). Locations are resolved from five
weighted signals with a confidence score; the Instagram geotag alone is never trusted because it
reflects the poster, not the job site.

Outputs per run: untouched raw API payloads (audit trail), pretty-printed processed JSON per
province, an append-only JSON Lines export, CSV, SQLite with a cross-run dedup index, and
entry-ready text files for the downstream form-filling tool.

## Application

Stages: discovery, fetch, parse, date filter, classify, OCR, normalise, deduplicate, store, plus
a separate cleaning stage. The OCR engine is RapidOCR (ONNX, pure pip) with the English
PP-OCRv4 recogniser; Tesseract is a drop-in alternative. OCR never fails a run: a missing engine
or a corrupt image downgrades one post to `skipped` or `failed` with its URLs intact.

The LLM reader runs on Groq's free tier, tries four models in order, cools a model down on a
429, caches answers by source text, and falls back to regex when no model can answer.

## Security

The scraper reads only what Instagram serves to a signed-out browser. It never logs in, solves
a CAPTCHA, or works around an access-control response; a 403, CAPTCHA, or login redirect is
terminal by policy. The robots.txt notice is logged at startup and an `enforce` mode makes the
run exit with zero requests. Whether running it complies with Instagram's Terms of Use is the
operator's decision, stated in the README.

## Result

The pipeline runs daily across provinces, with 314 offline tests guarding the extraction path.
Cross-run deduplication was verified live by re-running an identical scrape and writing zero
records. On a 24-post hand-labelled set the LLM cleaning path produced entry-ready rows for
every post; the regex-only path managed about one in five.

Reach is bounded by Instagram: since the 2026-09-04 login wall, an anonymous client sees the
twelve newest posts per account.
