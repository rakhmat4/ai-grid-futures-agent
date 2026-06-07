$ErrorActionPreference = "Stop"
& ".\.venv\Scripts\Activate.ps1"
Write-Host "Running Optuna for TRXUSDT: 300 trials" -ForegroundColor Cyan
python -m grid_agent.cli optimize-optuna --symbols TRXUSDT --timeframe 5m --trials 300
python -m grid_agent.cli report --symbols TRXUSDT --timeframe 5m
