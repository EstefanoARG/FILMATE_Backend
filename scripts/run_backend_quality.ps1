$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=xml -q

