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


class ProductionConfig(BaseConfig):
    PREFERRED_URL_SCHEME = "https"

    @classmethod
    def validate(cls) -> None:
        missing = [name for name in ("SECRET_KEY", "SITE_URL") if not os.environ.get(name)]
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
