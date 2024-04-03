FROM postgres:latest
# Copy the initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/init-db.sh
# Make sure the script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh
