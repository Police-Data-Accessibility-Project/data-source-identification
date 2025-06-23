#!/bin/sh

python apply_migrations.py
uvicorn src.api.main:app --host 0.0.0.0 --port 80
