# AI Grid Futures Agent

AI Grid Futures Agent adalah research engine open-source untuk menganalisis data pasar crypto futures dan mengeksplorasi konfigurasi **grid futures strategy** menggunakan **Optuna optimization**.

Project ini dibuat untuk alur:

```text
research → backtest → optimization → validation → paper trading → live kecil jika sudah benar-benar matang
```

> ⚠️ Project ini bukan nasihat keuangan. Jangan gunakan untuk live trading sebelum lolos validasi 3–6 bulan, walk-forward validation, dan paper trading.

## Status Saat Ini

Sistem sudah berhasil:

- Download data Binance USD-M Futures public OHLCV.
- Backtest neutral grid sederhana.
- Optimasi parameter dengan Optuna.
- Membuat pair leaderboard.
- Membuat HTML report.

Pair awal:

```text
ADAUSDT
XRPUSDT
TRXUSDT
```

Hasil eksperimen awal:

| Pair | Status | Catatan |
|---|---|---|
| TRXUSDT | IMPROVE_AND_RETEST | Risiko rendah, tetapi profit masih tipis |
| ADAUSDT | REJECT_STOPPED_OUT | Profit factor menarik, tetapi stopped out |
| XRPUSDT | REJECT_STOPPED_OUT | Win rate tinggi, tetapi stopped out dan fee kurang sehat |

Kesimpulan: **belum layak real market**. Project perlu upgrade V3: ATR adaptive grid, trend filter, walk-forward validation, dan funding simulation.

## Quick Start Windows

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\00_SETUP_WINDOWS.ps1
```

Download data:

```powershell
python -m grid_agent.cli download --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m --months 1
```

Backtest:

```powershell
python -m grid_agent.cli backtest --symbol ADAUSDT --timeframe 5m
```

Optuna test:

```powershell
python -m grid_agent.cli optimize-optuna --symbols ADAUSDT --timeframe 5m --trials 20
```

Report:

```powershell
python -m grid_agent.cli report --symbols ADAUSDT XRPUSDT TRXUSDT --timeframe 5m
```

## Kriteria Strategi Layak Lanjut

| Metrik | Target |
|---|---:|
| Net profit | Positif dan tidak terlalu tipis |
| Profit factor | > 1.25 |
| Max drawdown | < 10–15% |
| Trade count | > 50 |
| Risk score | < 0.35 |
| Stopped out | False |
| Walk-forward | Lolos |
| Paper trading | Stabil |

## Disclaimer

Project ini hanya untuk edukasi dan riset. Futures grid memiliki risiko leverage, liquidation, funding, fee drag, slippage, dan trend trap.
