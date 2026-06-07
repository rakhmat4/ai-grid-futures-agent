# PROMPT V3 — ATR Adaptive Grid and Trend Filter

Tempel prompt ini ke coding agent.

```text
Upgrade the AI Grid Futures Agent to V3.

Goal:
Improve the neutral grid futures research engine by adding adaptive volatility-based grid range and trend filtering.

Requirements:

1. Add ATR calculation using high, low, close. Default atr_period = 14.
2. Add ADX or simple trend strength proxy using EMA slope and normalized ATR.
3. Extend GridParams:
   - use_atr_range: bool = False
   - atr_period: int = 14
   - atr_multiplier: float = 4.0
   - trend_filter_enabled: bool = False
   - max_trend_strength: float = 25.0
   - min_grid_step_pct: float = 0.001
4. If use_atr_range is true:
   lower = center_price - ATR * atr_multiplier
   upper = center_price + ATR * atr_multiplier
5. If trend_filter_enabled is true, do not open new positions when trend strength is above threshold.
6. Update Optuna search space:
   - use_atr_range categorical [True, False]
   - atr_period int 10 to 30
   - atr_multiplier float 2.0 to 8.0
   - trend_filter_enabled categorical [True, False]
   - max_trend_strength float 18.0 to 35.0
   - range_pct float 0.01 to 0.10
   - grid_count int 8 to 50
   - order_fraction float 0.005 to 0.05
   - leverage float 1.0 to 2.0
   - stop_buffer_pct float 0.005 to 0.06
7. Update objective score:
   score =
      net_profit_pct
      - 1.8 * max_drawdown_pct
      + 0.05 * min(profit_factor, 5.0)
      - 0.45 * risk_score
      - (fee_cost / initial_capital) * 0.5
8. If stopped_out: score -= 0.5
9. If trade_count < 30: score -= 0.2
10. Add CLI command:
    python -m grid_agent.cli optimize-v3 --symbols TRXUSDT ADAUSDT XRPUSDT --timeframe 5m --trials 300
11. Update HTML report to show ATR and trend filter params.
12. Add tests.
13. Do not add live trading.
14. Keep everything research/backtest only.
```
