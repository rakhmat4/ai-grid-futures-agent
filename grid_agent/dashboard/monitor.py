"""Real-time monitoring dashboard using Streamlit."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
from datetime import datetime
from grid_agent.core.models import BacktestResult


class DashboardMonitor:
    """
    Real-time Streamlit dashboard for strategy monitoring.
    
    Features:
    - Live equity curve tracking
    - Win/loss statistics
    - Drawdown monitoring
    - Trade performance metrics
    - Risk indicators
    """
    
    def __init__(self):
        self.results: Dict[str, BacktestResult] = {}
    
    def add_result(self, symbol: str, result: BacktestResult) -> None:
        """
        Add backtest result to dashboard.
        """
        self.results[symbol] = result
    
    def render_dashboard(self) -> None:
        """
        Render main dashboard.
        """
        st.set_page_config(page_title="Grid Futures Agent", layout="wide")
        st.title("🤖 AI Grid Futures Agent - Dashboard")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "📈 Equity Curve",
            "🎯 Trades Analysis",
            "⚠️ Risk Metrics",
            "🔧 Configuration"
        ])
        
        with tab1:
            self.render_overview()
        
        with tab2:
            self.render_equity_curve()
        
        with tab3:
            self.render_trades_analysis()
        
        with tab4:
            self.render_risk_metrics()
        
        with tab5:
            self.render_configuration()
    
    def render_overview(self) -> None:
        """
        Render overview tab with summary statistics.
        """
        if not self.results:
            st.warning("No results loaded yet.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_trades = sum(r.total_trades for r in self.results.values())
        total_pnl = sum(r.net_profit for r in self.results.values())
        avg_win_rate = sum(r.win_rate for r in self.results.values()) / len(self.results) if self.results else 0
        avg_profit_factor = sum(r.profit_factor for r in self.results.values()) / len(self.results) if self.results else 0
        
        with col1:
            st.metric("Total Trades", total_trades)
        
        with col2:
            st.metric("Net Profit", f"${total_pnl:,.2f}")
        
        with col3:
            st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%")
        
        with col4:
            st.metric("Avg Profit Factor", f"{avg_profit_factor:.2f}")
        
        st.divider()
        
        # Results table
        st.subheader("Strategy Results by Symbol")
        results_data = []
        for symbol, result in self.results.items():
            results_data.append({
                'Symbol': symbol,
                'Trades': result.total_trades,
                'Win Rate': f"{result.win_rate:.1f}%",
                'Profit Factor': f"{result.profit_factor:.2f}",
                'Net Profit': f"${result.net_profit:,.2f}",
                'Max DD': f"{result.max_drawdown_pct:.2f}%",
                'Stopped Out': '❌' if result.stopped_out else '✅'
            })
        
        df = pd.DataFrame(results_data)
        st.dataframe(df, use_container_width=True)
    
    def render_equity_curve(self) -> None:
        """
        Render equity curve visualization.
        """
        if not self.results:
            st.warning("No results loaded yet.")
            return
        
        st.subheader("Equity Curve Over Time")
        
        # Create equity curve data
        for symbol, result in self.results.items():
            equity_values = [10000.0]
            
            for trade in result.trades:
                equity_values.append(equity_values[-1] + trade.pnl)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=equity_values,
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
            
            fig.update_layout(
                title=f"Equity Curve - {symbol}",
                xaxis_title="Trade #",
                yaxis_title="Equity ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_trades_analysis(self) -> None:
        """
        Render trades analysis tab.
        """
        if not self.results:
            st.warning("No results loaded yet.")
            return
        
        st.subheader("Trade Analysis")
        
        for symbol, result in self.results.items():
            st.write(f"### {symbol}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Winning Trades", result.winning_trades)
            
            with col2:
                st.metric("Losing Trades", result.losing_trades)
            
            with col3:
                st.metric("Avg Win", f"${result.avg_win:,.2f}")
            
            with col4:
                st.metric("Avg Loss", f"${result.avg_loss:,.2f}")
            
            # Win/Loss distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure(data=[
                    go.Bar(x=['Wins', 'Losses'], y=[result.winning_trades, result.losing_trades],
                           marker=dict(color=['green', 'red']))
                ])
                fig.update_layout(title="Win/Loss Distribution", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if result.total_trades > 0:
                    pnl_data = [t.pnl for t in result.trades]
                    fig = go.Figure(data=[go.Histogram(x=pnl_data, nbinsx=20)])
                    fig.update_layout(title="PnL Distribution", height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
    
    def render_risk_metrics(self) -> None:
        """
        Render risk metrics tab.
        """
        if not self.results:
            st.warning("No results loaded yet.")
            return
        
        st.subheader("Risk Metrics")
        
        for symbol, result in self.results.items():
            st.write(f"### {symbol}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Max Drawdown", f"{result.max_drawdown_pct:.2f}%")
            
            with col2:
                st.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")
            
            with col3:
                st.metric("Total Fees", f"${result.total_fees:,.2f}")
            
            with col4:
                st.metric("Funding Fees", f"${result.total_funding_fees:,.2f}")
            
            # Risk gauge
            risk_level = "🟢 Low" if result.max_drawdown_pct < 10 else "🟡 Medium" if result.max_drawdown_pct < 15 else "🔴 High"
            st.info(f"Risk Level: {risk_level}")
            
            st.divider()
    
    def render_configuration(self) -> None:
        """
        Render configuration tab.
        """
        st.subheader("Configuration")
        st.info("Configuration details coming soon...")
