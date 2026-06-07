"""Base grid strategy implementation."""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from grid_agent.core.models import Trade, BacktestResult, StrategyConfig
from grid_agent.indicators.trend import get_trend_signal
from grid_agent.indicators.atr import calculate_atr
from grid_agent.core.constants import (
    BINANCE_MAKER_FEE,
    BINANCE_TAKER_FEE,
    DEFAULT_FUNDING_FEE_DAILY,
)


class GridStrategy(ABC):
    """Abstract base class for grid strategies."""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.trades: List[Trade] = []
        self.active_positions: Dict[str, Dict] = {}  # Track open positions
        self.equity = 10000.0  # Starting equity
        self.peak_equity = 10000.0
        self.cumulative_funding_fees = 0.0
    
    @abstractmethod
    def generate_grid_levels(self, current_price: float, atr: Optional[float] = None) -> Tuple[List[float], List[float]]:
        """
        Generate buy and sell grid levels.
        
        Args:
            current_price: Current price
            atr: Optional ATR value for adaptive grid
        
        Returns:
            Tuple of (buy_levels, sell_levels)
        """
        pass
    
    def check_trend_filter(self, data: pd.DataFrame) -> bool:
        """
        Check if trend filter allows trading.
        
        Returns:
            True if trading is allowed, False otherwise
        """
        if not self.config.use_trend_filter:
            return True
        
        signal = get_trend_signal(
            data,
            filter_type=self.config.trend_filter_type,
            adx_period=self.config.adx_period,
            adx_threshold=self.config.adx_threshold,
            ma_fast_period=self.config.ma_fast_period,
            ma_slow_period=self.config.ma_slow_period,
            rsi_period=self.config.rsi_period,
            rsi_overbought=self.config.rsi_overbought,
            rsi_oversold=self.config.rsi_oversold,
        )
        
        return signal != 0  # Allow trading if signal is not neutral
    
    def backtest(self, data: pd.DataFrame, symbol: str, timeframe: str) -> BacktestResult:
        """
        Run backtest on historical data.
        
        Args:
            data: Historical OHLCV data
            symbol: Trading pair symbol
            timeframe: Timeframe string
        
        Returns:
            BacktestResult
        """
        self.trades = []
        self.active_positions = {}
        self.equity = 10000.0
        self.peak_equity = 10000.0
        self.cumulative_funding_fees = 0.0
        
        # Calculate ATR if adaptive grid is enabled
        atr_series = None
        if self.config.use_atr_adaptive:
            atr_series = calculate_atr(data, self.config.atr_period)
        
        # Iterate through candlesticks
        for i in range(self.config.grid_levels, len(data)):
            current_data = data.iloc[:i+1]
            current_row = data.iloc[i]
            current_price = current_row['close']
            current_time = current_row['timestamp'] if 'timestamp' in current_row else None
            
            # Check trend filter
            if not self.check_trend_filter(current_data):
                # Close all positions if trend filter rejects
                self._close_all_positions(current_price, current_time)
                continue
            
            # Get ATR value if available
            current_atr = atr_series.iloc[i] if atr_series is not None else None
            
            # Generate grid levels
            buy_levels, sell_levels = self.generate_grid_levels(current_price, current_atr)
            
            # Check for buy signals
            for level in buy_levels:
                if current_price <= level and f"buy_{level}" not in self.active_positions:
                    self._open_position("buy", current_price, current_time, level)
            
            # Check for sell signals
            for level in sell_levels:
                if current_price >= level and f"sell_{level}" not in self.active_positions:
                    self._open_position("sell", current_price, current_time, level)
            
            # Apply funding fees (hourly simulation)
            if i % 12 == 0:  # Every 12 candles (1 hour for 5m candles)
                self._apply_funding_fees(current_price)
            
            # Update equity
            self._update_equity(current_price)
        
        # Close remaining positions at end
        if len(data) > 0:
            last_price = data.iloc[-1]['close']
            self._close_all_positions(last_price, None)
        
        # Calculate result
        result = BacktestResult(symbol=symbol, timeframe=timeframe)
        result.trades = self.trades
        result.calculate_metrics()
        result.total_funding_fees = self.cumulative_funding_fees
        result.max_drawdown_pct = self._calculate_max_drawdown()
        
        return result
    
    def _open_position(self, side: str, price: float, time: datetime, level: float):
        """Open a new position."""
        position_size = (self.equity * self.config.position_size_pct / 100) / price
        position_key = f"{side}_{level}"
        
        self.active_positions[position_key] = {
            'side': side,
            'entry_price': price,
            'entry_time': time,
            'quantity': position_size,
            'level': level,
        }
    
    def _close_all_positions(self, current_price: float, current_time: datetime):
        """Close all active positions."""
        closed_positions = []
        for key, pos in self.active_positions.items():
            trade = Trade(
                entry_price=pos['entry_price'],
                exit_price=current_price,
                entry_time=pos['entry_time'],
                exit_time=current_time,
                side=pos['side'],
                quantity=pos['quantity'],
            )
            trade.calculate_pnl(self.config.maker_fee_pct, self.config.taker_fee_pct)
            self.trades.append(trade)
            closed_positions.append(key)
        
        for key in closed_positions:
            del self.active_positions[key]
    
    def _apply_funding_fees(self, current_price: float):
        """Apply funding fees to open positions."""
        daily_fee_pct = self.config.funding_fee_pct_daily / 100
        hourly_fee = daily_fee_pct / 24
        
        total_position_value = 0
        for pos in self.active_positions.values():
            total_position_value += pos['quantity'] * current_price
        
        funding_fee = total_position_value * hourly_fee
        self.cumulative_funding_fees += funding_fee
        self.equity -= funding_fee
    
    def _update_equity(self, current_price: float):
        """Update current equity based on open positions."""
        # Calculate unrealized PnL
        unrealized_pnl = 0
        for pos in self.active_positions.values():
            if pos['side'] == 'buy':
                unrealized_pnl += (current_price - pos['entry_price']) * pos['quantity']
            else:  # sell
                unrealized_pnl += (pos['entry_price'] - current_price) * pos['quantity']
        
        current_equity = 10000.0 + sum(t.pnl for t in self.trades) + unrealized_pnl - self.cumulative_funding_fees
        self.equity = max(current_equity, 0)  # Equity can't go below 0
        
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown percentage."""
        if not self.trades:
            return 0.0
        
        cumulative = 10000.0
        max_equity = 10000.0
        max_dd = 0.0
        
        for trade in self.trades:
            cumulative += trade.pnl
            max_equity = max(max_equity, cumulative)
            dd = (max_equity - cumulative) / max_equity * 100
            max_dd = max(max_dd, dd)
        
        return max_dd


class NeutralGridStrategy(GridStrategy):
    """Simple neutral grid strategy (fixed grid levels)."""
    
    def generate_grid_levels(self, current_price: float, atr: Optional[float] = None) -> Tuple[List[float], List[float]]:
        """
        Generate fixed grid levels around current price.
        """
        grid_spacing = current_price * 0.01  # 1% spacing
        
        buy_levels = []
        sell_levels = []
        
        half_levels = self.config.grid_levels // 2
        
        for i in range(1, half_levels + 1):
            buy_levels.append(current_price - (grid_spacing * i))
            sell_levels.append(current_price + (grid_spacing * i))
        
        return sorted(buy_levels), sorted(sell_levels, reverse=True)
