#!/bin/sh
uvicorn main:app --host 0.0.0.0 --port 9001 --workers 1
