"""Binance data fetcher for OHLCV data."""

import pandas as pd
import requests
from typing import List, Optional
from datetime import datetime, timedelta
from grid_agent.core.constants import (
    BINANCE_USD_M_FUTURES_URL,
    TIMEFRAME_MINUTES,
)
from grid_agent.core.utils import ensure_dir, get_data_dir
import os


class BinanceFetcher:
    """
    Fetch OHLCV data from Binance USD-M Futures public API.
    """
    
    def __init__(self):
        self.base_url = BINANCE_USD_M_FUTURES_URL
        self.data_dir = get_data_dir()
    
    def fetch_klines(self, symbol: str, timeframe: str, 
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     limit: int = 1000) -> pd.DataFrame:
        """
        Fetch candlestick data from Binance.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Max klines per request (1-1500)
        
        Returns:
            DataFrame with OHLCV data
        """
        all_klines = []
        endpoint = f"{self.base_url}/fapi/v1/klines"
        
        # Parse dates
        if start_date:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        else:
            start_ts = None
        
        if end_date:
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
        else:
            end_ts = int(datetime.now().timestamp() * 1000)
        
        current_ts = start_ts if start_ts else end_ts - (limit * TIMEFRAME_MINUTES.get(timeframe, 1) * 60 * 1000)
        
        while current_ts < end_ts:
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'startTime': current_ts,
                'endTime': end_ts,
                'limit': limit
            }
            
            try:
                response = requests.get(endpoint, params=params, timeout=10)
                response.raise_for_status()
                klines = response.json()
                
                if not klines:
                    break
                
                all_klines.extend(klines)
                
                # Move to next batch
                current_ts = klines[-1][0] + 1
                
                if len(klines) < limit:
                    break
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
        
        if not all_klines:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Clean up
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        df = df.reset_index(drop=True)
        
        return df
    
    def fetch_and_save(self, symbols: List[str], timeframe: str,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[str]:
        """
        Fetch data for multiple symbols and save to CSV.
        
        Args:
            symbols: List of symbols to fetch
            timeframe: Timeframe
            start_date: Start date
            end_date: End date
        
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        for symbol in symbols:
            print(f"Fetching {symbol} ({timeframe})...")
            df = self.fetch_klines(symbol, timeframe, start_date, end_date)
            
            if df.empty:
                print(f"No data for {symbol}")
                continue
            
            # Save to CSV
            filename = f"{symbol}_{timeframe}.csv"
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False)
            
            print(f"Saved {len(df)} candles to {filepath}")
            saved_files.append(filepath)
        
        return saved_files
    
    def load_from_csv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Load data from local CSV file.
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
        
        Returns:
            DataFrame with OHLCV data
        """
        filename = f"{symbol}_{timeframe}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
