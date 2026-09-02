"""SQLite persistence helpers for habits-cli."""

from pathlib import Path
import sqlite3


DEFAULT_DATABASE_PATH = Path("~/.habits-cli/habits.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    frequency TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_days INTEGER NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    UNIQUE (habit_id, completed_date),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);
"""


def get_connection(
    database_path: str | Path | None = None,
) -> sqlite3.Connection:
    """Open a SQLite database and ensure the application schema exists.

    When no path is supplied, the database is stored in
    ``~/.habits-cli/habits.db``. Passing ``":memory:"`` creates an isolated
    in-memory database, which is useful for tests.
    """
    if database_path is None:
        database_target = DEFAULT_DATABASE_PATH.expanduser()
        database_target.parent.mkdir(parents=True, exist_ok=True)
    elif str(database_path) == ":memory:":
        database_target = ":memory:"
    else:
        database_target = Path(database_path).expanduser()
        database_target.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.commit()
    return connection
