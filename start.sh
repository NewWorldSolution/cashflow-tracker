#!/bin/bash
cd "$(dirname "$0")"
python -m uvicorn app.main:app --reload &
sleep 2
open http://127.0.0.1:8000/
wait
