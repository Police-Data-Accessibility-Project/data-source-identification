#!/bin/sh

python apply_migrations.py
uvicorn api.main:app --host 0.0.0.0 --port 80
