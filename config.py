"""Configuration classes, selected by ``APP_ENV`` (development, testing, production)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class BaseConfig:
    SITE_NAME = "Ibnu Adzim · Case Room"
    SITE_SHORT_NAME = "Case Room"
    SITE_TAGLINE = "Cloud, DevOps, backend, data, and IoT case files"
    SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5000").rstrip("/")
    SECRET_KEY = os.environ.get("SECRET_KEY", "development-only-key")

    CONTENT_DIR = Path(os.environ.get("CONTENT_DIR", ROOT / "content"))
    STATIC_DIR = ROOT / "static"
    TEMPLATES_DIR = ROOT / "templates"

    CONTENT_RELOAD = False  # re-read content/ when files change (development only)
    SECURITY_HEADERS = True
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 365
    MAX_CONTENT_LENGTH = 1024 * 1024
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    CONTENT_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "testing-key"
    SITE_URL = "https://example.test"


VERCEL_URL_VARIABLES = ("VERCEL_PROJECT_PRODUCTION_URL", "VERCEL_URL")


def site_url_from_environment() -> str | None:
    """``SITE_URL`` if set; otherwise the hostname Vercel injects for the deployment."""
    explicit = os.environ.get("SITE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    for name in VERCEL_URL_VARIABLES:
        host = os.environ.get(name, "").strip()
        if host:
            return f"https://{host}".rstrip("/")
    return None


class ProductionConfig(BaseConfig):
    PREFERRED_URL_SCHEME = "https"

    @classmethod
    def validate(cls) -> None:
        missing = []
        if not os.environ.get("SECRET_KEY"):
            missing.append("SECRET_KEY")
        if not site_url_from_environment():
            missing.append("SITE_URL")
        if missing:
            raise RuntimeError(
                "production configuration is incomplete; set the environment variables: "
                + ", ".join(missing)
            )


CONFIGS: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[BaseConfig]:
    key = (name or os.environ.get("APP_ENV") or "development").strip().lower()
    try:
        return CONFIGS[key]
    except KeyError:
        raise RuntimeError(f"unknown APP_ENV {key!r}; expected one of {sorted(CONFIGS)}") from None
