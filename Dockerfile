# Dockerfile for Source Collector FastAPI app

FROM python:3.12.8

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 80

# Run Alembic migrations
CMD ["alembic", "upgrade", "head"]

## Run FastAPI app with uvicorn
#CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]