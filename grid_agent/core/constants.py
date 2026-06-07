"""Constants for grid futures agent."""

# Trading
BINANCE_USD_M_FUTURES_URL = "https://fapi.binance.com"
DEFAULT_TIMEFRAME = "5m"
DEFAULT_SYMBOLS = ["ADAUSDT", "XRPUSDT", "TRXUSDT"]

# Timeframe to minutes mapping
TIMEFRAME_MINUTES = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}

# ATR parameters
DEFAULT_ATR_PERIOD = 14
DEFAULT_ATR_MULTIPLIER = 1.5

# Trend filter parameters
DEFAULT_MA_FAST = 12
DEFAULT_MA_SLOW = 26
DEFAULT_ADX_PERIOD = 14
DEFAULT_ADX_THRESHOLD = 25.0
DEFAULT_RSI_PERIOD = 14

# Risk parameters
DEFAULT_MAX_DRAWDOWN_PCT = 15.0
DEFAULT_POSITION_SIZE_PCT = 1.0
DEFAULT_LEVERAGE = 1.0

# Fees
BINANCE_MAKER_FEE = 0.02  # 0.02%
BINANCE_TAKER_FEE = 0.04  # 0.04%
DEFAULT_FUNDING_FEE_DAILY = 0.01  # 0.01% daily
DEFAULT_SLIPPAGE_PCT = 0.05

# Stopped out thresholds
STOPPED_OUT_THRESHOLD = 0.03  # 3% consecutive loss

# Risk scoring weights (V3)
RISK_SCORE_WEIGHTS = {
    'drawdown': 0.3,
    'stopped_out': 0.4,
    'win_rate': 0.1,
    'profit_factor': 0.2,
}

# File paths
DATA_DIR = "data"
OUTPUT_DIR = "output"
REPORT_DIR = "reports"
MODELS_DIR = "models"

# Optuna
DEFAULT_OPTUNA_TRIALS = 100
DEFAULT_OPTUNA_JOBS = 4
