from __future__ import annotations

from sqlalchemy import create_engine

from .config import load_database_url


def make_engine(echo: bool = False):
    return create_engine(load_database_url(), echo=echo, future=True)
