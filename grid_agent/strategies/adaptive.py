"""Adaptive grid strategy using ATR."""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from grid_agent.strategies.grid import GridStrategy
from grid_agent.indicators.atr import get_adaptive_grid_spacing


class AdaptiveGridStrategy(GridStrategy):
    """ATR-based adaptive grid strategy.
    
    Grid spacing increases with volatility (ATR) and decreases with low volatility.
    This helps avoid being trapped in trending markets and captures more profit in range-bound markets.
    """
    
    def generate_grid_levels(self, current_price: float, atr: Optional[float] = None) -> Tuple[List[float], List[float]]:
        """
        Generate adaptive grid levels based on ATR.
        
        Args:
            current_price: Current price
            atr: ATR value
        
        Returns:
            Tuple of (buy_levels, sell_levels)
        """
        if atr is None or atr == 0:
            # Fallback to fixed grid if ATR not available
            grid_spacing = current_price * 0.01  # 1% spacing
        else:
            # Adaptive spacing based on ATR
            grid_spacing = get_adaptive_grid_spacing(atr, self.config.atr_multiplier)
        
        buy_levels = []
        sell_levels = []
        
        half_levels = self.config.grid_levels // 2
        
        for i in range(1, half_levels + 1):
            buy_levels.append(current_price - (grid_spacing * i))
            sell_levels.append(current_price + (grid_spacing * i))
        
        return sorted(buy_levels), sorted(sell_levels, reverse=True)
