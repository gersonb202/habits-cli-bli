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
    UNIQUE (habit_id, completed_date), -- Evitar duplicados
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);
"""


def get_connection(
    database_path: str | Path | None = None,
) -> sqlite3.Connection:
    # Verifica si la ruta no existe y crea los directorios necesarios
    if database_path is None:
        database_target = DEFAULT_DATABASE_PATH.expanduser()
        database_target.parent.mkdir(parents=True, exist_ok=True)
    elif str(database_path) == ":memory:":
        database_target = ":memory:"
    else:
        database_target = Path(database_path).expanduser()
        database_target.parent.mkdir(parents=True, exist_ok=True)

    # Crea la conexión a la base de datos SQLite y habilita las claves foráneas
    connection = sqlite3.connect(database_target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.commit()
    return connection


def insert_habit(
    connection: sqlite3.Connection,
    name: str,
    description: str | None,
) -> int:
    # Inserta un nuevo hábito y devuelve su identificador generado.
    cursor = connection.execute(
        "INSERT INTO habits (name, description) VALUES (?, ?)",
        (name, description),
    )
    connection.commit()
    return cursor.lastrowid


def get_habit(
    connection: sqlite3.Connection,
    habit_id: int,
) -> sqlite3.Row | None:
    # Devuelve un hábito por su identificador, o ``None`` si no existe.
    return connection.execute(
        "SELECT id, name, description FROM habits WHERE id = ?",
        (habit_id,),
    ).fetchone()


def insert_plan(
    connection: sqlite3.Connection,
    habit_id: int,
    frequency: str,
    start_date: str,
    end_date: str,
    total_days: int,
) -> int:
    # Inserta un nuevo plan de hábito y devuelve su identificador generado.
    cursor = connection.execute(
        "INSERT INTO plans "
        "(habit_id, frequency, start_date, end_date, total_days) "
        "VALUES (?, ?, ?, ?, ?)",
        (habit_id, frequency, start_date, end_date, total_days),
    )
    connection.commit()
    return cursor.lastrowid


def get_active_plan(
    connection: sqlite3.Connection,
    habit_id: int,
    today: str,
) -> sqlite3.Row | None:
    # Devuelve el plan activo más reciente para un hábito, o ``None`` si no hay ninguno.
    return connection.execute(
        "SELECT id, habit_id, frequency, start_date, end_date, total_days "
        "FROM plans "
        "WHERE habit_id = ? AND start_date <= ? AND end_date >= ? "
        "ORDER BY start_date DESC, id DESC LIMIT 1",
        (habit_id, today, today),
    ).fetchone()


def get_plan_by_habit(
    connection: sqlite3.Connection,
    habit_id: int,
) -> sqlite3.Row | None:
    # Devuelve el plan más reciente para un hábito, o ``None`` si no hay ninguno.
    return connection.execute(
        "SELECT id, habit_id, frequency, start_date, end_date, total_days "
        "FROM plans WHERE habit_id = ? "
        "ORDER BY start_date DESC, id DESC LIMIT 1",
        (habit_id,),
    ).fetchone()


def insert_completion(
    connection: sqlite3.Connection,
    habit_id: int,
    date: str,
) -> int:
    # Inserta un nuevo registro de finalización para un hábito y devuelve su identificador generado.
    cursor = connection.execute(
        "INSERT INTO completions (habit_id, completed_date) VALUES (?, ?)",
        (habit_id, date),
    )
    connection.commit()
    return cursor.lastrowid


def get_completion(
    connection: sqlite3.Connection,
    habit_id: int,
    date: str,
) -> sqlite3.Row | None:
    # Devuelve un registro de finalización para un hábito en una fecha específica, o ``None`` si no existe.
    return connection.execute(
        "SELECT id, habit_id, completed_date FROM completions "
        "WHERE habit_id = ? AND completed_date = ?",
        (habit_id, date),
    ).fetchone()


def count_completions(connection: sqlite3.Connection, habit_id: int) -> int:
    # Devuelve el número total de registros de finalización para un hábito.
    row = connection.execute(
        "SELECT COUNT(*) AS completion_count FROM completions "
        "WHERE habit_id = ?",
        (habit_id,),
    ).fetchone()
    return row["completion_count"]


def list_all_habits(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    # Devuelve todos los hábitos almacenados en la base de datos.
    return connection.execute(
        "SELECT id, name, description FROM habits ORDER BY id"
    ).fetchall()


def list_habits_with_active_plan(
    connection: sqlite3.Connection,
    today: str,
) -> list[sqlite3.Row]:
    # Devuelve todos los hábitos que tienen un plan activo en la fecha especificada.
    return connection.execute(
        "SELECT h.id, h.name, h.description, "
        "p.id AS plan_id, p.habit_id AS plan_habit_id, "
        "p.frequency, p.start_date, p.end_date, p.total_days "
        "FROM habits AS h "
        "JOIN plans AS p ON p.habit_id = h.id "
        "WHERE p.start_date <= ? AND p.end_date >= ? "
        "ORDER BY h.id, p.start_date DESC, p.id DESC",
        (today, today),
    ).fetchall()


def list_habits_without_plan(
    connection: sqlite3.Connection,
) -> list[sqlite3.Row]:
    # Devuelve todos los hábitos que no tienen ningún plan asociado.
    return connection.execute(
        "SELECT h.id, h.name, h.description FROM habits AS h "
        "WHERE NOT EXISTS ("
        "SELECT 1 FROM plans AS p WHERE p.habit_id = h.id"
        ") ORDER BY h.id"
    ).fetchall()
