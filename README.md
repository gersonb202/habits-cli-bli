# habits-cli

CLI local para crear, planificar y seguir hábitos directamente desde la terminal.

## Requisitos

- Python 3.12+

## Instalación (Nativa)

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

## Instalación con Docker

También puedes ejecutar la CLI utilizando Docker y Docker Compose, sin necesidad de instalar Python en tu máquina local.

**Características de la imagen Docker:**
- Utiliza `python:3.12-slim` en un *multi-stage build* para una imagen ligera y segura.
- Se ejecuta como usuario sin privilegios (`appuser`).
- Persistencia asegurada: utiliza un volumen nombrado de Docker (`habits-data`) mapeado a `/home/appuser/.habits-cli`, para que la base de datos no se pierda al detener el contenedor.

**Para construir la imagen:**
```bash
docker compose build
```

**Para ejecutar los comandos (usando `docker compose run`):**
```bash
docker compose run --rm habit new "Leer"
docker compose run --rm habit plan 1 -f daily --days 7
docker compose run --rm habit day
```
*Tip: Puedes crear un alias en tu sistema (ej. `alias habit='docker compose run --rm habit'`) para que se sienta como un comando local.*

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