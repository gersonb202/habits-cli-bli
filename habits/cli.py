import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import service, storage


app = typer.Typer(help="Gestiona tus hábitos desde la terminal.")


@app.callback()
def main() -> None:
    """Gestión de hábitos desde la terminal."""


@app.command("new")
def new(
    name: str = typer.Argument(..., help="Nombre del hábito."),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Descripción opcional del hábito.",
    ),
) -> None:
    connection = storage.get_connection()
    try:
        habit_id = service.create_habit(connection, name, description)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    finally:
        connection.close()

    typer.echo(f"¡Hábito creado con ID {habit_id}!")


@app.command("plan")
def plan(
    habit_id: int = typer.Argument(..., help="Identificador del hábito."),
    frequency: str = typer.Option(
        "daily",
        "--frequency",
        "-f",
        help="Frecuencia del plan.",
    ),
    days: int = typer.Option(
        ...,
        "--days",
        help="Duración del plan en días.",
    ),
) -> None:
    connection = storage.get_connection()
    try:
        created_plan = service.assign_plan(
            connection,
            habit_id,
            frequency,
            days,
        )
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    finally:
        connection.close()

    typer.echo(
        f"¡Plan creado para el hábito {created_plan.habit_id}! "
        f"({created_plan.start_date} a {created_plan.end_date})"
    )


@app.command("day")
def day() -> None:
    connection = storage.get_connection()
    try:
        habits = service.list_today(connection)
    finally:
        connection.close()

    if not habits:
        typer.echo("No hay hábitos, crea uno para empezar")
        return

    table = Table(title="Hábitos de hoy")
    table.add_column("ID")
    table.add_column("Hábito")
    table.add_column("Estado")
    for habit in habits:
        if habit.status == "completed":
            state = Text("[✓]")
        elif habit.status == "pending":
            state = Text("[ ]")
        else:
            state = Text("(por activar): crea el plan")
        table.add_row(str(habit.id), habit.name, state)

    Console().print(table)


@app.command("done")
def done(
    habit_id: int | None = typer.Argument(
        None,
        metavar="ID",
        help="Identificador del hábito.",
    ),
) -> None:
    if habit_id is None:
        typer.echo("Uso: habit done <id>", err=True)
        raise typer.Exit(code=1)

    connection = storage.get_connection()
    try:
        result = service.mark_done(connection, habit_id)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    finally:
        connection.close()

    messages = {
        "completed": "¡Hábito cumplido!",
        "already_completed": "¡Hábito ya cumplido, a por el siguiente!",
        "needs_plan": "El hábito necesita crear un plan primero.",
        "unavailable": "Hábito no disponible.",
    }
    typer.echo(messages[result.status])


def _progress_line(report: service.HabitReport, width: int = 16) -> Text:
    progress = max(0.0, min(report.progress, 1.0))
    filled_width = round(progress * width)
    line = Text(f"{report.id} {report.name} |")
    line.append("█" * filled_width, style="white")
    line.append("░" * (width - filled_width), style="dim")
    line.append(f"| {round(progress * 100)}%")
    return line


@app.command("report")
def report() -> None:
    connection = storage.get_connection()
    try:
        reports = service.get_report(connection)
    finally:
        connection.close()

    if not reports:
        typer.echo("No hay datos de progreso")
        return

    console = Console()
    for habit_report in reports:
        if habit_report.status == "unplanned":
            console.print(
                f"{habit_report.id} {habit_report.name} "
                "(por activar): crea el plan"
            )
        else:
            console.print(_progress_line(habit_report))


@app.command("celebrate")
def celebrate() -> None:
    connection = storage.get_connection()
    try:
        celebrations = service.get_celebrations(connection)
    finally:
        connection.close()

    if not celebrations:
        typer.echo("Aún no hay logros completados")
        return

    for celebration in celebrations:
        typer.echo(f"{celebration.name}: {celebration.message}")


if __name__ == "__main__":
    app()
