#!/bin/sh
exec uvicorn app.main:main_app.api --host 0.0.0.0 --port 8000
