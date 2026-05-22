"""Resolved paths for the investment chronicle."""

from __future__ import annotations

from pathlib import Path

_CHRONICLE_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = _CHRONICLE_ROOT / "data"
PRICES_DIR = DATA_DIR / "prices"
SITE_DIR = _CHRONICLE_ROOT / "site"
SITE_DATA_DIR = SITE_DIR / "data"
EXPORT_DIR = _CHRONICLE_ROOT / "export"


def repo_root() -> Path:
    return _REPO_ROOT


def chronicle_root() -> Path:
    return _CHRONICLE_ROOT
