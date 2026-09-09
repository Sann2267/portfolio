"""WSGI entry point: ``flask --app wsgi run``, ``gunicorn wsgi:app``, and the Vercel entrypoint."""

import sys
from pathlib import Path

# Serverless runtimes may import this file by path without putting its directory on
# sys.path; the ``app`` package and ``config`` module live next to it.
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app import create_app  # noqa: E402

app = create_app()
