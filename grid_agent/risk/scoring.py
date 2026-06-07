"""Risk scoring system for strategy evaluation."""

from typing import Dict
from grid_agent.core.models import BacktestResult
from grid_agent.core.constants import RISK_SCORE_WEIGHTS, STOPPED_OUT_THRESHOLD


class RiskScorer:
    """
    Comprehensive risk scoring system.
    
    Evaluates strategies on multiple risk dimensions:
    - Drawdown risk (30%)
    - Stopped out risk (40%)
    - Win rate reliability (10%)
    - Profit factor stability (20%)
    
    Final score: 0-1 (lower is better)
    Target: < 0.35 to pass validation
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or RISK_SCORE_WEIGHTS
    
    def calculate_risk_score(self, result: BacktestResult) -> Dict[str, float]:
        """
        Calculate comprehensive risk score.
        
        Args:
            result: BacktestResult from backtest
        
        Returns:
            Dict with component scores and total score
        """
        scores = {}
        
        # 1. Drawdown Risk Score (0-1, lower is better)
        scores['drawdown_score'] = self._calculate_drawdown_score(result.max_drawdown_pct)
        
        # 2. Stopped Out Risk Score (0-1, lower is better)
        scores['stopped_out_score'] = self._calculate_stopped_out_score(
            result.stopped_out_count,
            result.total_trades
        )
        
        # 3. Win Rate Score (0-1, higher is better - inverted for overall score)
        scores['win_rate_score'] = self._calculate_win_rate_score(result.win_rate)
        
        # 4. Profit Factor Score (0-1, higher is better - inverted for overall score)
        scores['profit_factor_score'] = self._calculate_profit_factor_score(result.profit_factor)
        
        # Calculate weighted total score
        total_score = (
            scores['drawdown_score'] * self.weights['drawdown'] +
            scores['stopped_out_score'] * self.weights['stopped_out'] +
            scores['win_rate_score'] * self.weights['win_rate'] +
            scores['profit_factor_score'] * self.weights['profit_factor']
        )
        
        scores['total_score'] = min(max(total_score, 0), 1)  # Clamp to 0-1
        scores['passes_validation'] = scores['total_score'] < 0.35
        
        return scores
    
    def _calculate_drawdown_score(self, max_dd_pct: float) -> float:
        """
        Calculate drawdown risk score.
        
        Target: < 10% = 0 (no risk)
        Warning: 10-15% = 0.3 (medium risk)
        Danger: > 15% = 1.0 (high risk)
        """
        if max_dd_pct < 10:
            return 0.0
        elif max_dd_pct < 15:
            return (max_dd_pct - 10) / 5 * 0.3
        elif max_dd_pct < 25:
            return 0.3 + (max_dd_pct - 15) / 10 * 0.7
        else:
            return 1.0
    
    def _calculate_stopped_out_score(self, stopped_out_count: int, total_trades: int) -> float:
        """
        Calculate stopped out risk score.
        
        Being stopped out means capital is locked and strategy failed.
        This is the most dangerous metric.
        
        0 stopped outs = 0 (pass)
        1+ stopped outs = 1 (fail)
        """
        if stopped_out_count == 0:
            return 0.0
        else:
            return 1.0  # Any stopped out = high risk
    
    def _calculate_win_rate_score(self, win_rate: float) -> float:
        """
        Calculate win rate score.
        
        Higher win rate = lower score (better)
        
        < 40% = 0.8 (risky)
        50% = 0.5 (neutral)
        > 60% = 0.0 (good)
        """
        if win_rate < 40:
            return 0.8
        elif win_rate < 50:
            return 0.8 - (win_rate - 40) / 10 * 0.3
        elif win_rate < 60:
            return 0.5 - (win_rate - 50) / 10 * 0.5
        else:
            return 0.0
    
    def _calculate_profit_factor_score(self, profit_factor: float) -> float:
        """
        Calculate profit factor score.
        
        Higher profit factor = lower score (better)
        
        < 1.0 = 1.0 (losing strategy)
        1.0-1.25 = 0.5 (marginal)
        > 1.25 = 0.0 (good)
        """
        if profit_factor < 1.0:
            return 1.0
        elif profit_factor < 1.25:
            return (1.25 - profit_factor) / 0.25 * 0.5
        else:
            return 0.0
    
    def get_validation_status(self, risk_score: Dict[str, float]) -> str:
        """
        Get human-readable validation status.
        """
        total_score = risk_score['total_score']
        
        if total_score < 0.20:
            return "EXCELLENT"
        elif total_score < 0.35:
            return "PASS"
        elif total_score < 0.50:
            return "IMPROVE_AND_RETEST"
        else:
            return "REJECT"
