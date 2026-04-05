"""
analytics.py — Core computation engine for MarketMind.
All financial metrics and data retrieval live here.
"""

import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats


class Analytics:
    def __init__(self):
        self.chart_style = {
            'bg': '#0d1117',
            'fg': '#e6edf3',
            'grid': '#21262d',
            'accent': '#58a6ff',
            'accent2': '#f78166',
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _default_range(self):
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        start = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        return start, end

    def _fetch(self, ticker, start=None, end=None):
        if start is None or end is None:
            s, e = self._default_range()
            start = start or s
            end = end or e
        data = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=True)
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker} in the given range.")
        return data

    def _daily_returns(self, ticker, start=None, end=None):
        data = self._fetch(ticker, start, end)
        returns = data['Close'].pct_change().dropna()
        if returns.empty:
            raise ValueError(f"Insufficient data for returns calculation on {ticker}.")
        return returns


    # ── Price Queries ───────────────────────────────────────────────────────────

    def fetch_price(self, ticker, on_date=None, for_year=None):
        """Return closing price for a ticker. Optionally constrained to date or year."""
        t = yf.Ticker(ticker)
        if on_date:
            next_day = (datetime.datetime.strptime(on_date, '%Y-%m-%d')
                        + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            data = t.history(start=on_date, end=next_day)
            if data.empty:
                return "No trading data for that date."
            price = round(data.iloc[0].Close, 4)
            last_date = data.index[0].strftime('%Y-%m-%d')
            return f"{price} (as of {last_date}). Data may be delayed."
        elif for_year:
            data = t.history(start=f"{for_year}-01-01", end=f"{for_year}-12-31")
            if data.empty:
                return "No data for that year."
            price = round(data.iloc[-1].Close, 4)
            return f"{price} (end of {for_year}). Data may be delayed."
        else:
            data = t.history(period='1y')
            price = round(data.iloc[-1].Close, 4)
            last_date = data.index[-1].strftime('%Y-%m-%d')
            return f"{price} (as of {last_date}). Data may be delayed."


    # ── Moving Averages ─────────────────────────────────────────────────────────

    def sma(self, ticker, period):
        """Simple Moving Average over `period` days."""
        closes = self._fetch(ticker)['Close']
        result = closes.rolling(window=int(period)).mean().iloc[-1]
        return str(round(result, 4))

    def ema(self, ticker, period):
        """Exponential Moving Average over `period` days."""
        closes = self._fetch(ticker)['Close']
        result = closes.ewm(span=int(period), adjust=False).mean().iloc[-1]
        return str(round(result, 4))


    # ── Momentum Indicators ────────────────────────────────────────────────────

    def rsi(self, ticker):
        """Relative Strength Index (14-day)."""
        closes = self._fetch(ticker)['Close']
        delta = closes.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.ewm(com=13, adjust=False).mean()
        avg_loss = losses.ewm(com=13, adjust=False).mean()
        rs = avg_gain / avg_loss
        return str(round((100 - 100 / (1 + rs)).iloc[-1], 4))

    def macd(self, ticker):
        """MACD line, signal line, and histogram — comma-separated."""
        closes = self._fetch(ticker)['Close']
        fast = closes.ewm(span=12, adjust=False).mean()
        slow = closes.ewm(span=26, adjust=False).mean()
        macd_line = fast - slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        return f"{round(macd_line.iloc[-1],4)}, {round(signal_line.iloc[-1],4)}, {round(histogram.iloc[-1],4)}"


    # ── Charting ────────────────────────────────────────────────────────────────

    def price_chart(self, ticker, start_date=None, end_date=None):
        """Plot closing price with a dark terminal aesthetic. Saves to price_chart.png."""
        s, e = self._default_range()
        start_date = start_date or s
        end_date = end_date or e
        data = self._fetch(ticker, start_date, end_date)

        fig, ax = plt.subplots(figsize=(11, 5))
        fig.patch.set_facecolor(self.chart_style['bg'])
        ax.set_facecolor(self.chart_style['bg'])

        ax.plot(data.index, data['Close'], color=self.chart_style['accent'], linewidth=1.6)
        ax.fill_between(data.index, data['Close'], alpha=0.12, color=self.chart_style['accent'])

        ax.set_title(f'{ticker}  ·  Close Price', color=self.chart_style['fg'],
                     fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('Date', color=self.chart_style['fg'], fontsize=9)
        ax.set_ylabel('Price (USD)', color=self.chart_style['fg'], fontsize=9)
        ax.tick_params(colors=self.chart_style['fg'])
        ax.grid(color=self.chart_style['grid'], linestyle='--', linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.chart_style['grid'])

        plt.tight_layout()
        plt.savefig('price_chart.png', dpi=130, facecolor=self.chart_style['bg'])
        plt.close()
        return "Chart saved to price_chart.png"

    def volatility_chart(self, ticker, start_date=None, end_date=None):
        """Plot 20-day rolling std-dev of returns. Saves to volatility_chart.png."""
        s, e = self._default_range()
        start_date = start_date or s
        end_date = end_date or e
        data = self._fetch(ticker, start_date, end_date)

        roll_vol = data['Close'].rolling(window=20).std()
        if roll_vol.dropna().empty:
            return "Insufficient data for rolling volatility."

        fig, ax = plt.subplots(figsize=(11, 4))
        fig.patch.set_facecolor(self.chart_style['bg'])
        ax.set_facecolor(self.chart_style['bg'])

        ax.plot(data.index, roll_vol, color=self.chart_style['accent2'], linewidth=1.4,
                label='20-day Rolling Vol')
        ax.set_title(f'{ticker}  ·  Rolling Volatility', color=self.chart_style['fg'],
                     fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('Date', color=self.chart_style['fg'], fontsize=9)
        ax.set_ylabel('Std Dev', color=self.chart_style['fg'], fontsize=9)
        ax.tick_params(colors=self.chart_style['fg'])
        ax.grid(color=self.chart_style['grid'], linestyle='--', linewidth=0.5)
        ax.legend(facecolor=self.chart_style['bg'], edgecolor=self.chart_style['grid'],
                  labelcolor=self.chart_style['fg'])
        for spine in ax.spines.values():
            spine.set_edgecolor(self.chart_style['grid'])

        plt.tight_layout()
        plt.savefig('volatility_chart.png', dpi=130, facecolor=self.chart_style['bg'])
        plt.close()
        return str(round(roll_vol.dropna().iloc[-1], 6))


    # ── Risk Metrics ────────────────────────────────────────────────────────────

    def daily_volatility(self, ticker, start_date=None, end_date=None):
        """Standard deviation of daily returns."""
        returns = self._daily_returns(ticker, start_date, end_date)
        return str(round(returns.std(), 6))

    def relative_vol(self, ticker_a, ticker_b, start_date=None, end_date=None):
        """Volatility difference: ticker_a minus ticker_b."""
        va = float(self.daily_volatility(ticker_a, start_date, end_date))
        vb = float(self.daily_volatility(ticker_b, start_date, end_date))
        return str(round(va - vb, 6))

    def sharpe(self, ticker, start_date, end_date, risk_free_rate=0.0):
        """Sharpe ratio given a risk-free rate (daily decimal)."""
        returns = self._daily_returns(ticker, start_date, end_date)
        excess = returns.mean() - risk_free_rate
        std = returns.std()
        if std == 0:
            return "Sharpe ratio undefined (zero volatility)."
        return str(round(excess / std, 4))

    def beta(self, ticker, benchmark, start_date=None, end_date=None):
        """Beta of ticker relative to benchmark via OLS."""
        r1 = self._daily_returns(ticker, start_date, end_date)
        r2 = self._daily_returns(benchmark, start_date, end_date)
        slope, *_ = stats.linregress(r2, r1)
        return str(round(slope, 4))

    def var(self, ticker, start_date, end_date, confidence=0.95):
        """Historical VaR at a given confidence level."""
        returns = self._daily_returns(ticker, start_date, end_date)
        result = np.percentile(returns, (1 - confidence) * 100)
        return str(round(result, 6))

    def max_drawdown(self, ticker, start_date=None, end_date=None):
        """Maximum peak-to-trough drawdown."""
        returns = self._daily_returns(ticker, start_date, end_date)
        cumret = (1 + returns).cumprod()
        peak = cumret.expanding().max()
        drawdown = (peak - cumret) / peak
        return str(round(drawdown.max(), 6))

    def annualized_return(self, ticker, start_date=None, end_date=None):
        """Annualized geometric return (252 trading days)."""
        returns = self._daily_returns(ticker, start_date, end_date)
        result = (1 + returns.mean()) ** 252 - 1
        return str(round(result, 6))

    def information_ratio(self, ticker, benchmark, start_date=None, end_date=None):
        """Active return / tracking error."""
        r1 = self._daily_returns(ticker, start_date, end_date)
        r2 = self._daily_returns(benchmark, start_date, end_date)
        active = r1 - r2
        te = active.std()
        if te == 0:
            return "Tracking error is zero — IR undefined."
        return str(round(active.mean() / te, 4))

    def rolling_corr(self, ticker_a, ticker_b, start_date=None, end_date=None):
        """20-day rolling correlation between two tickers (latest value)."""
        r1 = self._daily_returns(ticker_a, start_date, end_date)
        r2 = self._daily_returns(ticker_b, start_date, end_date)
        corr = r1.rolling(window=20).corr(r2).dropna()
        if corr.empty:
            return "Not enough data."
        return str(round(corr.iloc[-1], 4))

    def omega_ratio(self, ticker, start_date, end_date, threshold=0.0):
        """Omega ratio: wins above threshold / losses below threshold."""
        returns = self._daily_returns(ticker, start_date, end_date)
        wins = (returns > threshold).sum()
        losses = (returns < threshold).sum()
        if losses == 0:
            return "No negative returns — omega undefined."
        return str(round(wins / losses, 4))

    def r_squared(self, ticker, benchmark, start_date=None, end_date=None):
        """R² of ticker returns explained by benchmark returns."""
        r1 = self._daily_returns(ticker, start_date, end_date)
        r2 = self._daily_returns(benchmark, start_date, end_date)
        bv = r2.var()
        if bv == 0:
            return "Benchmark variance is zero — R² undefined."
        covar = np.cov(r1, r2)[0, 1]
        result = (covar / bv) ** 2
        return str(round(result, 6))

    def relative_return(self, ticker, benchmark, start_date=None, end_date=None):
        """Last-day excess return of ticker over benchmark."""
        r1 = self._daily_returns(ticker, start_date, end_date)
        r2 = self._daily_returns(benchmark, start_date, end_date)
        return str(round((r1 - r2).iloc[-1], 6))


    # ── Comparison Functions ────────────────────────────────────────────────────

    def compare_performance(self, tickers, start_date=None, end_date=None):
        perfs = {t: float(self.annualized_return(t, start_date, end_date)) for t in tickers}
        leader = max(perfs, key=perfs.get)
        msg = f"{leader} leads with annualized return of {round(perfs[leader]*100,2)}%."
        for t, v in perfs.items():
            if t != leader:
                msg += f" vs {t}: {round(v*100,2)}%."
        return msg

    def compare_risk(self, tickers, start_date=None, end_date=None):
        risks = {}
        for t in tickers:
            v = float(self.var(t, start_date or self._default_range()[0], end_date or self._default_range()[1]))
            d = float(self.max_drawdown(t, start_date, end_date))
            risks[t] = (v, d)
        riskiest = max(risks, key=lambda x: abs(risks[x][0]) + risks[x][1])
        v, d = risks[riskiest]
        return (f"{riskiest} carries the most risk: VaR={round(v,4)}, "
                f"Max Drawdown={round(d,4)}.")

    def compare_volatility(self, tickers, start_date=None, end_date=None):
        vols = {t: float(self.daily_volatility(t, start_date, end_date)) for t in tickers}
        most = max(vols, key=vols.get)
        msg = f"{most} is most volatile ({round(vols[most],4)})."
        for t, v in vols.items():
            if t != most:
                msg += f" {t}: {round(v,4)}."
        return msg

    def compare_relative_volatility(self, tickers, start_date=None, end_date=None):
        ref = tickers[0]
        rel = {t: float(self.relative_vol(ref, t, start_date, end_date)) for t in tickers[1:]}
        leader = max(rel, key=rel.get)
        return (f"{ref} has {round(rel[leader],4)} higher vol than {leader}.")

    def compare_rolling_volatility(self, tickers, start_date=None, end_date=None):
        rvols = {t: float(self.volatility_chart(t, start_date, end_date)) for t in tickers}
        most = max(rvols, key=rvols.get)
        return f"{most} shows highest rolling volatility ({round(rvols[most],4)})."


# Instantiate the analytics class
analytics = Analytics()

