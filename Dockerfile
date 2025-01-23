# Dockerfile for Source Collector FastAPI app

FROM python:3.12.8

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps

# Expose the application port
EXPOSE 80

RUN chmod +x execute.sh