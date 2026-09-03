# habits-cli

CLI local para crear, planificar y seguir hábitos directamente desde la terminal.

## Requisitos

- Python 3.12+

## Instalación

Se recomienda el uso de entornos virtuales:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

*Para entorno de desarrollo (con soporte para tests):*
```bash
pip install -e ".[dev]"
```

## Uso

El ejecutable principal es `habit`.

### Comandos

- **Crear hábito:**
  ```bash
  habit new <nombre> [-d <descripción>]
  ```
  Almacena un nuevo hábito y devuelve un identificador autoincremental.

- **Asignar plan:**
  ```bash
  habit plan <id> -f daily --days <N>
  ```
  Asigna un plan de cumplimiento diario. La duración debe ser mayor o igual a 1 día.

- **Hábitos del día:**
  ```bash
  habit day
  ```
  Muestra una tabla con los hábitos de hoy y su estado: pendiente `[ ]`, cumplido `[✓]` o `(por activar): crea el plan`.

- **Marcar cumplido:**
  ```bash
  habit done <id>
  ```
  Registra el cumplimiento del hábito para el día actual.

- **Informe de progreso:**
  ```bash
  habit report
  ```
  Visualiza una barra de progreso calculada en base a los días cumplidos / días totales del plan de cada hábito activo.

- **Celebrar logros:**
  ```bash
  habit celebrate
  ```
  Muestra los hábitos que han alcanzado el 100 % de cumplimiento de su plan.

## Arquitectura y Stack Técnico

Proyecto estructurado en 3 capas estrictas (para mantener la lógica separada de la CLI):
1. `cli.py`: Comandos y presentación visual (sin lógica de negocio).
2. `service.py`: Reglas de negocio y validaciones. No interactúa directamente con la UI ni con la DB.
3. `storage.py`: Capa de persistencia.

**Stack:**
- **Python 3.12+**
- **Typer**: Manejo de interfaz de línea de comandos.
- **Rich**: Tablas, barras de progreso y renderizado en terminal.
- **SQLite**: Persistencia local (uso estricto de SQL nativo sin ORMs).
- **pytest**: Framework para tests automatizados.

## Persistencia de datos

La base de datos SQLite se crea y gestiona automáticamente. Por defecto reside en:
`~/.habits-cli/habits.db`

No requiere configuración previa.