# Use a base image with PostgreSQL tools
FROM postgres:15

# Optional: Set the working directory
WORKDIR /dump

# Ensure bash and other useful tools are installed
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy a script to handle the dump process
COPY dump.sh /usr/local/bin/dump.sh
COPY restore.sh /usr/local/bin/restore.sh
RUN chmod +x /usr/local/bin/dump.sh
RUN chmod +x /usr/local/bin/restore.sh

# Default command (can be overridden)
CMD ["bash"]
