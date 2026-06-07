"""ATR (Average True Range) indicator."""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        period: ATR period (default: 14)
    
    Returns:
        ATR values as Series
    """
    high = data['high'].values
    low = data['low'].values
    close = data['close'].values
    
    # Calculate True Range
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    tr[0] = tr1[0]  # First TR = H - L
    
    # Calculate ATR using RMA (exponential moving average)
    atr = pd.Series(tr).rolling(window=period).mean()
    
    # Smooth with exponential average for more responsive ATR
    atr = atr.ewm(span=period, adjust=False).mean()
    
    return atr


def calculate_atr_bands(data: pd.DataFrame, period: int = 14, multiplier: float = 1.5) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate ATR-based bands for adaptive grid sizing.
    
    Args:
        data: DataFrame with OHLCV data
        period: ATR period
        multiplier: ATR multiplier for band width
    
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    atr = calculate_atr(data, period)
    close = data['close']
    
    middle = close
    upper = middle + (atr * multiplier)
    lower = middle - (atr * multiplier)
    
    return upper, middle, lower


def get_adaptive_grid_spacing(atr_value: float, multiplier: float = 1.5) -> float:
    """
    Get adaptive grid spacing based on ATR.
    
    Higher ATR = wider grid spacing (more volatility)
    Lower ATR = tighter grid spacing (less volatility)
    
    Args:
        atr_value: Current ATR value
        multiplier: ATR multiplier
    
    Returns:
        Grid spacing percentage
    """
    return atr_value * multiplier
