from dataclasses import dataclass
from datetime import date, timedelta
import sqlite3

from . import storage


CELEBRATION_MESSAGE = "¡Enhorabuena! Has completado tu hábito."


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
    status: str = "active"


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


def _as_date(value: date | str | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def assign_plan(
    connection: sqlite3.Connection,
    habit_id: int,
    frequency: str,
    days: int,
    today: date | str | None = None,
) -> Plan:
    if days < 1:
        raise ValueError("Los días deben ser mayores o iguales a 1.")

    habit = storage.get_habit(connection, habit_id)
    if habit is None:
        raise ValueError("Hábito no encontrado.")

    start_date = _as_date(today)
    start_date_text = start_date.isoformat()
    if storage.get_active_plan(connection, habit_id, start_date_text) is not None:
        raise ValueError("El hábito ya tiene un plan activo.")

    end_date_text = (start_date + timedelta(days=days - 1)).isoformat()
    plan_id = storage.insert_plan(
        connection,
        habit_id,
        frequency,
        start_date_text,
        end_date_text,
        days,
    )
    return Plan(
        id=plan_id,
        habit_id=habit_id,
        frequency=frequency,
        start_date=start_date_text,
        end_date=end_date_text,
        total_days=days,
    )


def list_today(
    connection: sqlite3.Connection,
    today: date | str | None = None,
) -> list[TodayHabit]:
    today_text = _as_date(today).isoformat()
    today_habits: list[TodayHabit] = []

    for habit in storage.list_all_habits(connection):
        plan = storage.get_active_plan(connection, habit["id"], today_text)
        if plan is None:
            if storage.get_plan_by_habit(connection, habit["id"]) is not None:
                continue
            status = "unplanned"
        elif storage.get_completion(connection, habit["id"], today_text) is not None:
            status = "completed"
        else:
            status = "pending"

        today_habits.append(
            TodayHabit(
                id=habit["id"],
                name=habit["name"],
                description=habit["description"],
                status=status,
            )
        )

    return today_habits


def mark_done(
    connection: sqlite3.Connection,
    habit_id: int,
    today: date | str | None = None,
) -> TodayHabit:
    habit = storage.get_habit(connection, habit_id)
    if habit is None:
        raise ValueError("Hábito no encontrado.")

    today_text = _as_date(today).isoformat()
    plan = storage.get_active_plan(connection, habit_id, today_text)
    if plan is None:
        status = (
            "needs_plan"
            if storage.get_plan_by_habit(connection, habit_id) is None
            else "unavailable"
        )
    elif storage.get_completion(connection, habit_id, today_text) is not None:
        status = "already_completed"
    else:
        storage.insert_completion(connection, habit_id, today_text)
        status = "completed"

    return TodayHabit(
        id=habit["id"],
        name=habit["name"],
        description=habit["description"],
        status=status,
    )


def get_report(
    connection: sqlite3.Connection,
    today: date | str | None = None,
) -> list[HabitReport]:
    today_text = _as_date(today).isoformat()
    reports: list[HabitReport] = []

    for habit in storage.list_all_habits(connection):
        plan = storage.get_active_plan(connection, habit["id"], today_text)
        if plan is None:
            if storage.get_plan_by_habit(connection, habit["id"]) is not None:
                continue
            reports.append(
                HabitReport(
                    id=habit["id"],
                    name=habit["name"],
                    completed_days=0,
                    total_days=0,
                    progress=0.0,
                    description=habit["description"],
                    status="unplanned",
                )
            )
            continue

        completed_days = storage.count_completions(connection, habit["id"])
        total_days = plan["total_days"]
        reports.append(
            HabitReport(
                id=habit["id"],
                name=habit["name"],
                completed_days=completed_days,
                total_days=total_days,
                progress=completed_days / total_days,
                description=habit["description"],
                status="active",
            )
        )

    return reports


def get_celebrations(
    connection: sqlite3.Connection,
    today: date | str | None = None,
) -> list[HabitCelebration]:
    today_text = _as_date(today).isoformat()
    celebrations: list[HabitCelebration] = []

    for habit in storage.list_all_habits(connection):
        plan = storage.get_plan_by_habit(connection, habit["id"])
        if plan is None:
            continue

        active_plan = storage.get_active_plan(connection, habit["id"], today_text)
        if active_plan is not None:
            if active_plan["end_date"] != today_text:
                continue
            current_plan = active_plan
        elif plan["end_date"] >= today_text:
            continue
        else:
            current_plan = plan

        completed_days = storage.count_completions(connection, habit["id"])
        if completed_days != current_plan["total_days"]:
            continue

        celebrations.append(
            HabitCelebration(
                id=habit["id"],
                name=habit["name"],
                message=CELEBRATION_MESSAGE,
            )
        )

    return celebrations
