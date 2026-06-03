#!/usr/bin/env python3
"""Simple debug health check — runs BEFORE main app."""
import sys, os

print("Python:", sys.version)
print("CWD:", os.getcwd())
print("PORT env:", os.getenv("PORT", "not set"))

# Test imports
try:
    import fastapi; print("fastapi:", fastapi.__version__)
except Exception as e: print("fastapi FAIL:", e); sys.exit(1)

try:
    import uvicorn; print("uvicorn:", uvicorn.__version__)
except Exception as e: print("uvicorn FAIL:", e); sys.exit(1)

try:
    from pycryptodome import Crypto; print("pycryptodome: OK")
except Exception as e: print("pycryptodome FAIL:", e); sys.exit(1)

try:
    import requests; print("requests:", requests.__version__)
except Exception as e: print("requests FAIL:", e); sys.exit(1)

print("All imports OK. Starting main...")
exec(open("main.py").read())
