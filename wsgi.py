"""WSGI entry point: ``flask --app wsgi run``, ``gunicorn wsgi:app``, and the Vercel entrypoint."""

from app import create_app

app = create_app()
