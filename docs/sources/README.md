# docs/sources

Source material used to write the case content. Everything in this folder except this README is
ignored by git and must stay out of the public repository.

Expected files (kept locally only):

| File | Used for |
|---|---|
| `Modul - DevOps Automation.pdf` | Case 003 — TechnoDev DevOps CI/CD Platform |
| `Modul - Cloud Ai, Data Analytics.pdf` | Case 004 — NusaCommerce Analytics Platform |
| `Modul - Infrastructure as Service.pdf` | Case 005 — Multi-Tenant SaaS Infrastructure |
| `Monitoring IoT ESP32 & AWS.pdf` | Case 006 — ESP32 + AWS IoT Monitoring (image-only PDF) |

Why ignored: the three cloud modules are LKS National Competition task briefs. Only content derived
from them (in `content/`) is published, with the competition context stated on each case.

Extraction notes: `pdfplumber` (with `pypdfium2`) under Python 3.12 extracts the text layer of the
three cloud modules and can rasterize image-only pages to PNG for visual transcription. Extraction
scripts are run from a scratch directory and are not committed.
