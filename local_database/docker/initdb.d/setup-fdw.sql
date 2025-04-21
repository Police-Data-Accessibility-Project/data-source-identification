-- This script connects to db_b and sets up FDW access to db_a
\connect source_collector_test_db;

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER db_a_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'localhost', dbname 'db_a');

CREATE USER MAPPING FOR test_source_collector_user
  SERVER db_a_server
  OPTIONS (user 'test_source_collector_user', password 'HanviliciousHamiltonHilltops');

-- Example: import tables from db_a (assuming public schema exists and has tables)
IMPORT FOREIGN SCHEMA public FROM SERVER db_a_server INTO foreign_a;
