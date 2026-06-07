"""Trend indicators: ADX, MA Cross, RSI."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict


def calculate_adx(data: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate ADX (Average Directional Index) with +DI and -DI.
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        period: ADX period (default: 14)
    
    Returns:
        Tuple of (ADX, +DI, -DI)
    """
    high = data['high'].values
    low = data['low'].values
    close = data['close'].values
    
    # Calculate directional movements
    up_move = high[1:] - high[:-1]
    down_move = low[:-1] - low[1:]
    
    # Apply directional movement rules
    plus_dm = np.zeros(len(high))
    minus_dm = np.zeros(len(high))
    
    for i in range(1, len(high)):
        if up_move[i-1] > down_move[i-1] and up_move[i-1] > 0:
            plus_dm[i] = up_move[i-1]
        if down_move[i-1] > up_move[i-1] and down_move[i-1] > 0:
            minus_dm[i] = down_move[i-1]
    
    # Calculate True Range
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    tr = np.concatenate(([high[0] - low[0]], tr))
    
    # Calculate average values
    atr_series = pd.Series(tr).rolling(window=period).mean()
    plus_dm_series = pd.Series(plus_dm).rolling(window=period).mean()
    minus_dm_series = pd.Series(minus_dm).rolling(window=period).mean()
    
    # Calculate DI values
    plus_di = (plus_dm_series / atr_series * 100).fillna(0)
    minus_di = (minus_dm_series / atr_series * 100).fillna(0)
    
    # Calculate DX
    di_sum = plus_di + minus_di
    di_sum = di_sum.replace(0, 0.0001)  # Avoid division by zero
    dx = (np.abs(plus_di - minus_di) / di_sum * 100).fillna(0)
    
    # Calculate ADX
    adx = pd.Series(dx).rolling(window=period).mean()
    adx = adx.ewm(span=period, adjust=False).mean()
    
    return adx, plus_di, minus_di


def calculate_ma_cross(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26) -> Dict[str, pd.Series]:
    """
    Calculate Moving Average Crossover signals.
    
    Args:
        data: DataFrame with 'close' column
        fast_period: Fast MA period
        slow_period: Slow MA period
    
    Returns:
        Dict with 'fast_ma', 'slow_ma', 'signal' (-1, 0, 1)
    """
    close = data['close']
    
    fast_ma = close.rolling(window=fast_period).mean()
    slow_ma = close.rolling(window=slow_period).mean()
    
    # Generate signals: 1 = bullish, -1 = bearish, 0 = neutral
    signal = pd.Series(0, index=close.index)
    signal[fast_ma > slow_ma] = 1
    signal[fast_ma < slow_ma] = -1
    
    return {
        'fast_ma': fast_ma,
        'slow_ma': slow_ma,
        'signal': signal,
    }


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index).
    
    Args:
        data: DataFrame with 'close' column
        period: RSI period (default: 14)
    
    Returns:
        RSI values (0-100)
    """
    close = data['close']
    delta = close.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss.replace(0, 0.0001)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50)  # Fill initial NaN with neutral value


def get_trend_signal(data: pd.DataFrame, filter_type: str = "adx", **kwargs) -> int:
    """
    Get trend signal based on selected filter type.
    
    Args:
        data: DataFrame with OHLCV data
        filter_type: "adx", "ma_cross", "rsi", or "combination"
        **kwargs: Additional parameters for each filter
    
    Returns:
        Signal: 1 (bullish), -1 (bearish), 0 (neutral)
    """
    if filter_type == "adx":
        adx_threshold = kwargs.get('adx_threshold', 25.0)
        adx, plus_di, minus_di = calculate_adx(data, kwargs.get('adx_period', 14))
        
        last_adx = adx.iloc[-1]
        last_plus_di = plus_di.iloc[-1]
        last_minus_di = minus_di.iloc[-1]
        
        if last_adx > adx_threshold:
            return 1 if last_plus_di > last_minus_di else -1
        return 0
    
    elif filter_type == "ma_cross":
        ma_result = calculate_ma_cross(data, kwargs.get('fast_period', 12), kwargs.get('slow_period', 26))
        return int(ma_result['signal'].iloc[-1])
    
    elif filter_type == "rsi":
        rsi = calculate_rsi(data, kwargs.get('rsi_period', 14))
        last_rsi = rsi.iloc[-1]
        overbought = kwargs.get('rsi_overbought', 70.0)
        oversold = kwargs.get('rsi_oversold', 30.0)
        
        if last_rsi > overbought:
            return -1  # Bearish
        elif last_rsi < oversold:
            return 1   # Bullish
        return 0
    
    elif filter_type == "combination":
        # Combine ADX, MA Cross, and RSI for more robust signal
        adx_signal = get_trend_signal(data, "adx", **kwargs)
        ma_signal = get_trend_signal(data, "ma_cross", **kwargs)
        rsi_signal = get_trend_signal(data, "rsi", **kwargs)
        
        # Majority vote
        total_signal = adx_signal + ma_signal + rsi_signal
        if total_signal > 0:
            return 1
        elif total_signal < 0:
            return -1
        return 0
    
    return 0
