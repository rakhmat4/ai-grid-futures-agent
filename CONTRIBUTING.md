# Contributing

Project ini adalah research/backtest engine, bukan live trading bot.

Kontribusi yang diprioritaskan:

- risk control
- validation
- realistic fee/funding/slippage simulation
- testing
- documentation

Jalankan test sebelum pull request:

```powershell
pytest
```

Jangan tambahkan dulu:

- real order execution
- API key handling untuk live trading
- high leverage default
- klaim profit/garansi win rate
