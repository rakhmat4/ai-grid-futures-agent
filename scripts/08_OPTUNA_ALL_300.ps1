$ErrorActionPreference = "Stop"
& ".\.venv\Scripts\Activate.ps1"
Write-Host "Running Optuna for all pairs: 300 trials each" -ForegroundColor Cyan
python -m grid_agent.cli optimize-optuna --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m --trials 300
python -m grid_agent.cli report --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m
