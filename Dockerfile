# --- Etapa de build ---
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml .
COPY habits/ habits/

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home appuser

# Copiar dependencias instaladas desde la etapa de build
COPY --from=builder /install /usr/local

# Copiar código fuente
WORKDIR /app
COPY habits/ habits/

# Cambiar a usuario sin privilegios
USER appuser

# Crear directorio de datos con permisos del usuario
RUN mkdir -p /home/appuser/.habits-cli

ENTRYPOINT ["habit"]
