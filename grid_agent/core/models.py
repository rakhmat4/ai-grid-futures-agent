"""Data models for grid futures agent."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd


@dataclass
class OHLCVData:
    """OHLCV candlestick data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }


@dataclass
class StrategyConfig:
    """Grid futures strategy configuration."""
    # Grid parameters
    grid_levels: int = 10
    grid_type: str = "neutral"  # neutral, long, short
    
    # ATR parameters (V3)
    use_atr_adaptive: bool = True
    atr_period: int = 14
    atr_multiplier: float = 1.5
    
    # Trend filter parameters (V3)
    use_trend_filter: bool = True
    trend_filter_type: str = "adx"  # adx, ma_cross, rsi, combination
    ma_fast_period: int = 12
    ma_slow_period: int = 26
    adx_period: int = 14
    adx_threshold: float = 25.0
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    
    # Risk parameters
    max_drawdown_pct: float = 15.0
    position_size_pct: float = 1.0
    leverage: float = 1.0
    
    # Fee parameters (V4)
    maker_fee_pct: float = 0.02
    taker_fee_pct: float = 0.04
    funding_fee_pct_daily: float = 0.01  # Daily funding fee
    
    # Slippage (V4)
    slippage_pct: float = 0.05
    
    # Other
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None


@dataclass
class Trade:
    """Single trade record."""
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    side: str  # buy or sell
    quantity: float
    fees: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    stopped_out: bool = False
    
    def calculate_pnl(self, maker_fee: float, taker_fee: float) -> None:
        """Calculate PnL with fees."""
        gross_pnl = (self.exit_price - self.entry_price) * self.quantity
        self.fees = (self.entry_price * self.quantity * maker_fee + 
                     self.exit_price * self.quantity * taker_fee) / 100
        self.pnl = gross_pnl - self.fees
        self.pnl_pct = (self.pnl / (self.entry_price * self.quantity)) * 100


@dataclass
class BacktestResult:
    """Backtest results."""
    symbol: str
    timeframe: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    stopped_out_count: int = 0
    stopped_out: bool = False
    avg_trade: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    total_fees: float = 0.0
    total_funding_fees: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    
    def calculate_metrics(self) -> None:
        """Calculate all metrics from trades."""
        if not self.trades:
            return
        
        self.total_trades = len(self.trades)
        self.winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        self.losing_trades = sum(1 for t in self.trades if t.pnl < 0)
        
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        self.gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        self.gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        self.net_profit = sum(t.pnl for t in self.trades)
        
        if self.gross_loss > 0:
            self.profit_factor = self.gross_profit / self.gross_loss
        
        self.total_fees = sum(t.fees for t in self.trades)
        self.stopped_out_count = sum(1 for t in self.trades if t.stopped_out)
        self.stopped_out = self.stopped_out_count > 0
        
        if self.winning_trades > 0:
            self.avg_win = self.gross_profit / self.winning_trades
        
        if self.losing_trades > 0:
            self.avg_loss = self.gross_loss / self.losing_trades
        
        if self.total_trades > 0:
            self.avg_trade = self.net_profit / self.total_trades
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round(self.win_rate, 2),
            'gross_profit': round(self.gross_profit, 2),
            'gross_loss': round(self.gross_loss, 2),
            'net_profit': round(self.net_profit, 2),
            'profit_factor': round(self.profit_factor, 2),
            'max_drawdown_pct': round(self.max_drawdown_pct, 2),
            'stopped_out': self.stopped_out,
            'stopped_out_count': self.stopped_out_count,
            'avg_trade': round(self.avg_trade, 2),
            'avg_win': round(self.avg_win, 2),
            'avg_loss': round(self.avg_loss, 2),
            'total_fees': round(self.total_fees, 2),
            'total_funding_fees': round(self.total_funding_fees, 2),
        }
