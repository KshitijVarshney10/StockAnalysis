"""
test_analytics.py — Unit tests for analytics.py
"""

import pytest
from analytics import analytics


def test_fetch_price():
    result = analytics.fetch_price("AAPL")
    assert "AAPL" in result or "No data" in result


def test_sma():
    result = analytics.sma("AAPL", 50)
    assert isinstance(float(result), float)


def test_daily_volatility():
    result = analytics.daily_volatility("AAPL")
    assert isinstance(float(result), float)


def test_sharpe_zero_vol():
    # Mock or test edge case
    pass  # Add proper test


if __name__ == "__main__":
    pytest.main()