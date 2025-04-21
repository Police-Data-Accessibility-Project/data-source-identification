#!/bin/bash

set -euo pipefail

# Defaults (can be overridden)
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
DB_A="${DB_A:-db_a}"
DB_B="${DB_B:-db_b}"

export PGPASSWORD="$POSTGRES_PASSWORD"

echo "Creating databases $DB_A and $DB_B..."
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -p "$POSTGRES_PORT" -c "CREATE DATABASE $DB_A;" || echo "$DB_A already exists"
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -p "$POSTGRES_PORT" -c "CREATE DATABASE $DB_B;" || echo "$DB_B already exists"

echo "Setting up FDW in $DB_B to access $DB_A..."
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$DB_B" -p "$POSTGRES_PORT" <<EOF
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

DROP SERVER IF EXISTS db_a_server CASCADE;
CREATE SERVER db_a_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '$POSTGRES_HOST', dbname '$DB_A', port '$POSTGRES_PORT');

CREATE USER MAPPING IF NOT EXISTS FOR $POSTGRES_USER
  SERVER db_a_server
  OPTIONS (user '$POSTGRES_USER', password '$POSTGRES_PASSWORD');

-- Optional: import public schema into "foreign_a" schema in db_b
DROP SCHEMA IF EXISTS foreign_a CASCADE;
CREATE SCHEMA foreign_a;
IMPORT FOREIGN SCHEMA public FROM SERVER db_a_server INTO foreign_a;
EOF

echo "✅ FDW setup complete!"
