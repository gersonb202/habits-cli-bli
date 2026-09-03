from dataclasses import dataclass
import sqlite3

from . import storage


@dataclass(frozen=True)
class Habit:

    id: int
    name: str
    description: str | None = None


@dataclass(frozen=True)
class Plan:

    id: int
    habit_id: int
    frequency: str
    start_date: str
    end_date: str
    total_days: int


@dataclass(frozen=True)
class TodayHabit:

    id: int
    name: str
    status: str
    description: str | None = None


@dataclass(frozen=True)
class HabitReport:

    id: int
    name: str
    completed_days: int
    total_days: int
    progress: float
    description: str | None = None


@dataclass(frozen=True)
class HabitCelebration:

    id: int
    name: str
    message: str


def create_habit(
    connection: sqlite3.Connection,
    name: str,
    description: str | None = None,
) -> int:
    # Crea un nuevo hábito y devuelve su identificador generado.
    if not name or not name.strip():
        raise ValueError("El nombre es obligatorio.")
    if len(name) > 100:
        raise ValueError("El nombre no puede superar los 100 caracteres.")
    if description is not None and len(description) > 500:
        raise ValueError(
            "La descripción no puede superar los 500 caracteres."
        )

    return storage.insert_habit(connection, name, description)
