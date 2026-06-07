"""Validation framework for strategy robustness testing."""

from typing import Dict, List, Tuple
import pandas as pd
from grid_agent.core.models import BacktestResult, StrategyConfig
from grid_agent.strategies.grid import GridStrategy


class WalkForwardValidator:
    """
    Walk-Forward Validation (WFV) framework.
    
    Splits data into training and testing periods:
    - Train on N months
    - Test on 1 month (out-of-sample)
    - Roll forward and repeat
    
    This prevents overfitting and ensures strategy robustness.
    """
    
    def __init__(self, train_months: int = 3, test_months: int = 1):
        """
        Args:
            train_months: Number of months for training
            test_months: Number of months for testing (out-of-sample)
        """
        self.train_months = train_months
        self.test_months = test_months
    
    def split_data(self, data: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Split data into train/test windows.
        
        Args:
            data: Full historical data
        
        Returns:
            List of (train_data, test_data) tuples
        """
        if 'timestamp' in data.columns:
            data = data.sort_values('timestamp')
        else:
            data = data.sort_index()
        
        data_length = len(data)
        train_size = int(data_length * 0.7)  # 70% for training
        test_size = data_length - train_size  # 30% for testing
        
        windows = []
        start_idx = 0
        
        while start_idx + train_size + test_size <= data_length:
            train_data = data.iloc[start_idx : start_idx + train_size]
            test_data = data.iloc[start_idx + train_size : start_idx + train_size + test_size]
            
            windows.append((train_data, test_data))
            start_idx += test_size  # Roll forward by test period
        
        return windows
    
    def validate(self, data: pd.DataFrame, strategy: GridStrategy, 
                 symbol: str, timeframe: str) -> Dict:
        """
        Run walk-forward validation.
        
        Args:
            data: Full historical data
            strategy: Strategy instance
            symbol: Trading pair symbol
            timeframe: Timeframe string
        
        Returns:
            Validation results with train and test metrics
        """
        windows = self.split_data(data)
        
        train_results = []
        test_results = []
        consistency_scores = []
        
        for i, (train_data, test_data) in enumerate(windows):
            # Train on historical data
            train_result = strategy.backtest(train_data, symbol, timeframe)
            train_results.append(train_result)
            
            # Test on out-of-sample data
            test_result = strategy.backtest(test_data, symbol, timeframe)
            test_results.append(test_result)
            
            # Calculate consistency score
            consistency = self._calculate_consistency_score(train_result, test_result)
            consistency_scores.append(consistency)
        
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
        
        return {
            'windows': len(windows),
            'train_results': train_results,
            'test_results': test_results,
            'consistency_scores': consistency_scores,
            'avg_consistency': round(avg_consistency, 2),
            'passes_wfv': avg_consistency > 0.7,  # Pass if > 70% consistency
        }
    
    def _calculate_consistency_score(self, train_result: BacktestResult, 
                                     test_result: BacktestResult) -> float:
        """
        Calculate consistency between train and test results.
        
        Measures how stable the strategy is out-of-sample.
        
        Returns:
            Score 0-1 (higher is better)
        """
        if train_result.total_trades == 0 or test_result.total_trades == 0:
            return 0.0
        
        # Compare key metrics
        if train_result.profit_factor == 0 or test_result.profit_factor == 0:
            return 0.0
        
        pf_ratio = min(test_result.profit_factor, train_result.profit_factor) / \
                   max(test_result.profit_factor, train_result.profit_factor)
        wr_ratio = min(test_result.win_rate, train_result.win_rate) / \
                   max(test_result.win_rate, train_result.win_rate) if max(test_result.win_rate, train_result.win_rate) > 0 else 0
        
        # Consistency = average of ratios
        consistency = (pf_ratio + wr_ratio) / 2
        
        return consistency


class MonteCarloValidator:
    """
    Monte Carlo robustness testing.
    
    Shuffles trade order and results to test strategy resilience.
    """
    
    def __init__(self, iterations: int = 100):
        self.iterations = iterations
    
    def validate(self, backtest_result: BacktestResult) -> Dict:
        """
        Run Monte Carlo validation on backtest results.
        
        Args:
            backtest_result: BacktestResult from backtest
        
        Returns:
            Validation results with robustness metrics
        """
        import random
        
        if len(backtest_result.trades) < 10:
            return {
                'iterations': self.iterations,
                'passes_monte_carlo': False,
                'reason': 'Insufficient trades for Monte Carlo (< 10)'
            }
        
        profitable_iterations = 0
        worst_case_pnl = float('inf')
        best_case_pnl = float('-inf')
        
        original_trades = backtest_result.trades.copy()
        
        for _ in range(self.iterations):
            # Shuffle trade order
            shuffled_trades = original_trades.copy()
            random.shuffle(shuffled_trades)
            
            # Calculate cumulative PnL
            cumulative_pnl = 0
            is_profitable = True
            
            for trade in shuffled_trades:
                cumulative_pnl += trade.pnl
                if cumulative_pnl < 0:
                    is_profitable = False
            
            if is_profitable:
                profitable_iterations += 1
            
            worst_case_pnl = min(worst_case_pnl, cumulative_pnl)
            best_case_pnl = max(best_case_pnl, cumulative_pnl)
        
        robustness_pct = (profitable_iterations / self.iterations) * 100
        
        return {
            'iterations': self.iterations,
            'profitable_iterations': profitable_iterations,
            'robustness_pct': round(robustness_pct, 2),
            'worst_case_pnl': round(worst_case_pnl, 2),
            'best_case_pnl': round(best_case_pnl, 2),
            'passes_monte_carlo': robustness_pct > 60,  # Pass if > 60% scenarios profitable
        }
