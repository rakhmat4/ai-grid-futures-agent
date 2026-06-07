"""Risk management for live trading."""

from typing import Dict, Optional
from datetime import datetime


class RiskManager:
    """
    Risk management system for live/paper trading.
    
    Features:
    - Position size limits
    - Drawdown monitoring
    - Daily loss limits
    - Leverage guards
    """
    
    def __init__(self, initial_capital: float, max_daily_loss_pct: float = 5.0, 
                 max_drawdown_pct: float = 15.0, max_leverage: float = 3.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_leverage = max_leverage
        
        self.peak_capital = initial_capital
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
    
    def can_trade(self) -> bool:
        """
        Check if trading is allowed based on risk parameters.
        """
        # Check daily loss limit
        if abs(self.daily_pnl) > (self.initial_capital * self.max_daily_loss_pct / 100):
            return False
        
        # Check drawdown limit
        current_dd_pct = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
        if current_dd_pct > self.max_drawdown_pct:
            return False
        
        return True
    
    def calculate_position_size(self, current_price: float, account_balance: float, 
                                risk_pct: float = 1.0) -> float:
        """
        Calculate position size based on risk percentage and current leverage.
        
        Args:
            current_price: Current price of asset
            account_balance: Current account balance
            risk_pct: Risk percentage per trade (default 1%)
        
        Returns:
            Position size in quantity
        """
        risk_amount = account_balance * (risk_pct / 100)
        position_size = risk_amount / current_price
        
        return position_size
    
    def update_pnl(self, trade_pnl: float) -> None:
        """
        Update capital and daily PnL after a trade.
        """
        self.current_capital += trade_pnl
        self.daily_pnl += trade_pnl
        
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
    
    def reset_daily_stats(self) -> None:
        """
        Reset daily statistics.
        """
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
    
    def get_current_drawdown_pct(self) -> float:
        """
        Get current drawdown percentage.
        """
        if self.peak_capital == 0:
            return 0.0
        return ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
    
    def get_stats(self) -> Dict:
        """
        Get current risk stats.
        """
        return {
            'current_capital': round(self.current_capital, 2),
            'peak_capital': round(self.peak_capital, 2),
            'current_drawdown_pct': round(self.get_current_drawdown_pct(), 2),
            'daily_pnl': round(self.daily_pnl, 2),
            'can_trade': self.can_trade(),
        }
