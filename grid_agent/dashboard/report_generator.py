"""HTML and text report generator."""

import os
from datetime import datetime
from typing import List, Dict
from grid_agent.core.models import BacktestResult
from grid_agent.core.utils import get_report_dir, get_timestamp_string


class ReportGenerator:
    """
    Generate comprehensive HTML and text reports.
    """
    
    def __init__(self):
        self.report_dir = get_report_dir()
    
    def generate_html_report(self, results: List[BacktestResult], 
                             title: str = "Strategy Backtest Report") -> str:
        """
        Generate comprehensive HTML report.
        
        Args:
            results: List of BacktestResult
            title: Report title
        
        Returns:
            Path to generated HTML file
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    padding: 40px;
                }}
                h1 {{
                    color: #667eea;
                    margin-bottom: 10px;
                }}
                h2 {{
                    color: #764ba2;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .timestamp {{
                    color: #999;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                tr:hover {{
                    background: #f5f5f5;
                }}
                .pass {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .fail {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .warning {{
                    color: #ffc107;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #999;
                    font-size: 0.9em;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 {title}</h1>
                <div class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                
                <h2>Summary</h2>
                {self._generate_summary_section(results)}
                
                <h2>Detailed Results</h2>
                {self._generate_detailed_section(results)}
                
                <div class="footer">
                    <p>⚠️ Disclaimer: This report is for educational purposes only. Not financial advice. Always conduct thorough validation before live trading.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML file
        timestamp = get_timestamp_string()
        filename = f"report_{timestamp}.html"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_summary_section(self, results: List[BacktestResult]) -> str:
        """
        Generate summary metrics section.
        """
        total_trades = sum(r.total_trades for r in results)
        total_pnl = sum(r.net_profit for r in results)
        avg_win_rate = sum(r.win_rate for r in results) / len(results) if results else 0
        avg_profit_factor = sum(r.profit_factor for r in results) / len(results) if results else 0
        
        html = f"""
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{total_trades}</div>
                <div class="metric-label">Total Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${total_pnl:,.0f}</div>
                <div class="metric-label">Net Profit</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_win_rate:.1f}%</div>
                <div class="metric-label">Avg Win Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_profit_factor:.2f}</div>
                <div class="metric-label">Avg Profit Factor</div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_detailed_section(self, results: List[BacktestResult]) -> str:
        """
        Generate detailed results table.
        """
        html = "<table><tr>"
        html += "<th>Symbol</th><th>Trades</th><th>Win Rate</th><th>Profit Factor</th>"
        html += "<th>Net Profit</th><th>Max DD</th><th>Avg Trade</th><th>Status</th></tr>"
        
        for result in results:
            status_class = "pass" if result.profit_factor > 1.25 and not result.stopped_out else "fail"
            status_text = "✅ PASS" if status_class == "pass" else "❌ FAIL"
            
            html += f"""
            <tr>
                <td><strong>{result.symbol}</strong></td>
                <td>{result.total_trades}</td>
                <td>{result.win_rate:.1f}%</td>
                <td>{result.profit_factor:.2f}</td>
                <td>${result.net_profit:,.2f}</td>
                <td>{result.max_drawdown_pct:.2f}%</td>
                <td>${result.avg_trade:,.2f}</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def generate_text_report(self, result: BacktestResult) -> str:
        """
        Generate plain text report.
        """
        report = f"""
╔════════════════════════════════════════════════════════════╗
║         AI Grid Futures Agent - Backtest Report           ║
╚════════════════════════════════════════════════════════════╝

Symbol: {result.symbol}
Timeframe: {result.timeframe}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

┌─── TRADE STATISTICS ───────────────────────────────────────┐
│ Total Trades:        {result.total_trades:>6}                           │
│ Winning Trades:      {result.winning_trades:>6}                           │
│ Losing Trades:       {result.losing_trades:>6}                           │
│ Win Rate:            {result.win_rate:>6.2f}%                          │
│ Consecutive Wins:    {result.consecutive_wins:>6}                           │
│ Consecutive Losses:  {result.consecutive_losses:>6}                           │
└────────────────────────────────────────────────────────────┘

┌─── PROFIT & LOSS ──────────────────────────────────────────┐
│ Gross Profit:        ${result.gross_profit:>15,.2f}        │
│ Gross Loss:          ${result.gross_loss:>15,.2f}        │
│ Net Profit:          ${result.net_profit:>15,.2f}        │
│ Profit Factor:       {result.profit_factor:>6.2f}                           │
│ Avg Trade:           ${result.avg_trade:>15,.2f}        │
│ Avg Win:             ${result.avg_win:>15,.2f}        │
│ Avg Loss:            ${result.avg_loss:>15,.2f}        │
└────────────────────────────────────────────────────────────┘

┌─── RISK METRICS ──────────────────────────────────────────┐
│ Max Drawdown:        {result.max_drawdown_pct:>6.2f}%                          │
│ Sharpe Ratio:        {result.sharpe_ratio:>6.2f}                           │
│ Total Fees:          ${result.total_fees:>15,.2f}        │
│ Funding Fees:        ${result.total_funding_fees:>15,.2f}        │
│ Stopped Out:         {'YES ❌' if result.stopped_out else 'NO ✅':>20}       │
│ Stopped Out Count:   {result.stopped_out_count:>6}                           │
└────────────────────────────────────────────────────────────┘

⚠️  DISCLAIMER:
This report is for educational purposes only. Not financial advice.
Always conduct thorough validation before live trading.

"""
        return report
