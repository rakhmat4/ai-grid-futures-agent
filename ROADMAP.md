# ROADMAP

## V1 — Starter Research Engine
Status: selesai.

- Binance public OHLCV downloader
- Neutral grid backtester
- Basic risk metrics
- CLI
- HTML report

## V2 — Optuna Altcoins
Status: selesai.

- Optuna optimizer
- ADAUSDT, XRPUSDT, TRXUSDT
- Pair leaderboard
- Best strategy JSON
- Trials CSV

## V3 — Adaptive Grid and Trend Filter
Status: next build.

Target:

- ATR-based adaptive grid
- ADX / trend strength filter
- Volatility no-trade filter
- Stronger stopped-out penalty
- Stronger fee penalty
- Optimize V3 command

Target command:

```powershell
python -m grid_agent.cli optimize-v3 --symbols TRXUSDT ADAUSDT XRPUSDT --timeframe 5m --trials 300
```

## V4 — Validation Layer

- Train/test split
- Walk-forward validation
- Monte Carlo robustness check
- Funding fee simulation

## V5 — Paper Trading

- Live data stream
- Paper position state
- Daily report
- No real order execution

## V6 — Execution Guard

- Manual approval
- Testnet first
- Kill switch
- Max daily loss
- Max leverage guard
- Isolated margin only
