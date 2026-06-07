# Experiment 001 — Optuna Altcoins 5m

## Setup

- Symbols: ADAUSDT, XRPUSDT, TRXUSDT
- Timeframe: 5m
- Data: 1 month
- Optimizer: Optuna
- Strategy: neutral grid futures research backtest

## Result

| Symbol | Status | Interpretation |
|---|---|---|
| TRXUSDT | IMPROVE_AND_RETEST | Best candidate for further research, but profit still thin |
| ADAUSDT | REJECT_STOPPED_OUT | Strategy escaped grid range |
| XRPUSDT | REJECT_STOPPED_OUT | High win rate but weak robustness |

## Decision

No real market execution.

## Next Step

```powershell
python -m grid_agent.cli download --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m --months 3
python -m grid_agent.cli optimize-optuna --symbols TRXUSDT --timeframe 5m --trials 300
```

Then upgrade to V3.
