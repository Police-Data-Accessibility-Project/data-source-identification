#!/bin/bash
set -e

# Variables (customize these or pass them as environment variables)
DB_HOST=${RESTORE_HOST:-"postgres_container"}
DB_USER=${RESTORE_USER:-"your_user"}
DB_PORT=${RESTORE_PORT:-"5432"}  # Default to 5432 if not provided
DB_PASSWORD=${RESTORE_PASSWORD:-"your_password"}
NEW_DB_NAME=${RESTORE_DB_NAME:-"new_database"} # Name of the database to restore into
DUMP_FILE=${DUMP_FILE:-"/dump/db_dump.sql"}

MAINTENANCE_DB="postgres"

# Export password for pg_restore
export PGPASSWORD=$DB_PASSWORD

CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$NEW_DB_NAME"
MAINT_CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$MAINTENANCE_DB"

echo "Checking if database $NEW_DB_NAME exists on $DB_HOST:$DB_PORT..."
psql -d $MAINT_CONNECTION_STRING -tc "SELECT 1 FROM pg_database WHERE datname = '$NEW_DB_NAME';" | grep -q 1 && {
    echo "Database $NEW_DB_NAME exists. Dropping it..."
    # Terminate all connections to the database
    psql -d $MAINT_CONNECTION_STRING -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$NEW_DB_NAME';"
    # Drop the database
    psql -d $MAINT_CONNECTION_STRING -c "DROP DATABASE $NEW_DB_NAME;"
}

# Create the new database
echo "Creating new database $NEW_DB_NAME on $DB_HOST:$DB_PORT..."
psql -d $MAINT_CONNECTION_STRING -c "CREATE DATABASE $NEW_DB_NAME;" || {
    echo "Failed to create database $NEW_DB_NAME. It might already exist."
    exit 1
}

# Restore the dump into the new database
echo "Restoring dump from $DUMP_FILE into database $NEW_DB_NAME..."
pg_restore -d $CONNECTION_STRING --no-owner --no-acl -F c $DUMP_FILE

echo "Database restoration completed."
