"""Utility helpers for the hatchery project."""
from datetime import datetime


def now_utc():
    return datetime.utcnow()
