"""PostgreSQL connection pool for KesfetPlus.

Replaces the `threading.Lock` + JSON-file pattern every store module used to
follow (see database/README.md) - comments/checkins/status/users/sessions/
reports/push_subscriptions now live in real tables (database/schema.sql),
and every store function in this package talks to them through
`get_cursor()` below instead of reading/writing a *.json file.

Lazy on purpose: the connection pool is only created on the *first* call
that actually needs a connection (get_cursor()), not at import time. This
matters because every store module (and therefore api/main.py, which
imports all of them at startup) must still be importable even when
DATABASE_URL isn't set yet - e.g. local dev before PostgreSQL is installed,
or `ruff`/`mypy` just importing the package to check it. Calling a store
function that actually needs the database *will* raise
DatabaseNotConfiguredError in that case (there is, genuinely, no database to
talk to - this is not a fake/placeholder success), but with an actionable
message, at the point of use, not as a mysterious crash on `import`.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

if TYPE_CHECKING:
    from typing import Any

    from psycopg import Cursor

_pool_lock = threading.Lock()
_pool: ConnectionPool | None = None


class DatabaseNotConfiguredError(RuntimeError):
    """Raised when a store function needs a DB connection but DATABASE_URL
    isn't set (or no server is actually listening at that address) - see
    .env.example."""


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is None:
            dsn = os.getenv("DATABASE_URL")
            if not dsn:
                raise DatabaseNotConfiguredError(
                    "DATABASE_URL ortam değişkeni tanımlı değil. .env dosyana gerçek bir "
                    "PostgreSQL bağlantı adresi ekle (bkz. .env.example). Yerel geliştirme "
                    "için Docker ile tek satırda bir Postgres ayağa kaldırabilirsin:\n"
                    "  docker run --name kesfetplus-pg -e POSTGRES_PASSWORD=devpassword "
                    "-p 5432:5432 -d postgres:16\n"
                    "ardından:\n"
                    "  DATABASE_URL=postgresql://postgres:devpassword@localhost:5432/postgres\n"
                    "ve database/schema.sql'i o veritabanına uygula."
                )
            # open=False + explicit .open(): avoids psycopg_pool's own
            # "opened a pool in the constructor" deprecation/implicit-IO
            # warning, and keeps pool creation itself lazy/explicit here.
            _pool = ConnectionPool(dsn, min_size=1, max_size=10, open=False)
            _pool.open()
    return _pool


@contextmanager
def get_cursor() -> Iterator[Cursor[dict[str, Any]]]:
    """One DB transaction, one dict-row cursor.

    Every statement run through the yielded cursor belongs to the same
    transaction: it commits as a whole when the `with` block exits
    normally, and rolls back as a whole if the block raises - this is what
    replaces the old `with _lock: data = _load(); ...; _save(data)` pattern
    (and, unlike a `threading.Lock`, it stays correct across multiple
    worker processes, not just multiple threads in one).

    Rows come back as plain dicts (column name -> value), matching the
    shape every store function already returned when it was reading a JSON
    file.
    """
    pool = _get_pool()
    with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        yield cur
