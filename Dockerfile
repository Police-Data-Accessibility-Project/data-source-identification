# Dockerfile for Source Collector FastAPI app

FROM python:3.11.9-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

COPY pyproject.toml uv.lock ./

# Install dependencies
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked --no-dev
# Must call from the root directory because uv does not add playwright to path
RUN playwright install-deps chromium
RUN playwright install chromium

# Copy project files
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY apply_migrations.py ./apply_migrations.py
COPY execute.sh ./execute.sh
COPY .project-root ./.project-root

# Expose the application port
EXPOSE 80

RUN chmod +x execute.sh
# Use the below for ease of local development, but remove when pushing to GitHub
# Because there is no .env file in the repository (for security reasons)
#COPY .env ./.env
