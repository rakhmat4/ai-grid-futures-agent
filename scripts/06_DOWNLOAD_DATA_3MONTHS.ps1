$ErrorActionPreference = "Stop"
& ".\.venv\Scripts\Activate.ps1"
Write-Host "Downloading 3 months data: ADAUSDT XRPUSDT TRXUSDT 5m" -ForegroundColor Cyan
python -m grid_agent.cli download --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m --months 3
