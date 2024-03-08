#!/bin/sh
exec poetry run uvicorn app.main:main_app.api --host 0.0.0.0 --port 8000
