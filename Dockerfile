# Dockerfile for Source Collector FastAPI app

FROM python:3.12.8

# Set working directory
WORKDIR /app

COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps

# Copy project files
COPY agency_identifier ./agency_identifier
COPY api ./api
COPY collector_db ./collector_db
COPY collector_manager ./collector_manager
COPY core ./core
COPY html_tag_collector ./html_tag_collector
COPY hugging_face/url_relevance ./hugging_face/url_relevance
COPY hugging_face/HuggingFaceInterface.py ./hugging_face/HuggingFaceInterface.py
COPY source_collectors ./source_collectors
COPY util ./util
COPY alembic.ini ./alembic.ini
COPY apply_migrations.py ./apply_migrations.py
COPY security_manager ./security_manager
COPY execute.sh ./execute.sh
COPY .project-root ./.project-root

# Expose the application port
EXPOSE 80

COPY .env ./.env
RUN chmod +x execute.sh