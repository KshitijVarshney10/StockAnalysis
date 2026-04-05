"""
tool_schemas.py — OpenAI function-calling schemas for MarketMind tools.
"""

TOOL_SCHEMAS = [

    {
        "name": "fetch_price",
        "description": "Retrieves the closing stock price for a given ticker. Can target a specific date or year.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. 'TSLA' for Tesla."
                },
                "on_date": {
                    "type": "string",
                    "description": "Specific date in YYYY-MM-DD format. Omit for latest price."
                },
                "for_year": {
                    "type": "string",
                    "description": "Four-digit year, e.g. '2022'. Returns end-of-year closing price."
                }
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "sma",
        "description": "Calculates the Simple Moving Average (SMA) for a stock over a given period in trading days.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."},
                "period": {"type": "integer", "description": "Rolling window in days (e.g. 50 or 200)."}
            },
            "required": ["ticker", "period"]
        }
    },

    {
        "name": "ema",
        "description": "Calculates the Exponential Moving Average (EMA) for a stock over a given span.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."},
                "period": {"type": "integer", "description": "EMA span in days."}
            },
            "required": ["ticker", "period"]
        }
    },

    {
        "name": "rsi",
        "description": "Computes the 14-day Relative Strength Index (RSI) for a stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "macd",
        "description": "Returns MACD line, signal line, and histogram (comma-separated) for a stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "price_chart",
        "description": "Plots closing price history for a stock. Saves a dark-themed chart to price_chart.png.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."},
                "start_date": {"type": "string", "description": "Start date YYYY-MM-DD (default: 1 year ago)."},
                "end_date": {"type": "string", "description": "End date YYYY-MM-DD (default: today)."}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "volatility_chart",
        "description": "Plots 20-day rolling volatility for a stock and saves to volatility_chart.png.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol."},
                "start_date": {"type": "string", "description": "Start date YYYY-MM-DD."},
                "end_date": {"type": "string", "description": "End date YYYY-MM-DD."}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "daily_volatility",
        "description": "Returns the standard deviation of daily returns for a stock over a date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "relative_vol",
        "description": "Computes the difference in daily volatility between two stocks (ticker_a minus ticker_b).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_a": {"type": "string", "description": "First stock ticker."},
                "ticker_b": {"type": "string", "description": "Second stock ticker."},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker_a", "ticker_b"]
        }
    },

    {
        "name": "sharpe",
        "description": "Calculates the Sharpe ratio for a stock. Requires date range and risk-free rate.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string", "description": "Start date YYYY-MM-DD."},
                "end_date": {"type": "string", "description": "End date YYYY-MM-DD."},
                "risk_free_rate": {
                    "type": "number",
                    "description": "Daily risk-free rate as a decimal (e.g. 0.0001). Defaults to 0."
                }
            },
            "required": ["ticker", "start_date", "end_date"]
        }
    },

    {
        "name": "beta",
        "description": "Calculates the beta of a stock relative to a benchmark (e.g. SPY).",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "benchmark": {"type": "string", "description": "Benchmark ticker, e.g. 'SPY'."},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker", "benchmark"]
        }
    },

    {
        "name": "var",
        "description": "Historical Value at Risk (VaR) at a given confidence level.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "confidence": {
                    "type": "number",
                    "description": "Confidence level as decimal (e.g. 0.95 for 95%). Defaults to 0.95."
                }
            },
            "required": ["ticker", "start_date", "end_date"]
        }
    },

    {
        "name": "max_drawdown",
        "description": "Calculates the maximum peak-to-trough drawdown of a stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "annualized_return",
        "description": "Computes the annualized geometric return (252-day) for a stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker"]
        }
    },

    {
        "name": "information_ratio",
        "description": "Calculates the information ratio (active return / tracking error) for a stock vs. a benchmark.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "benchmark": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker", "benchmark"]
        }
    },

    {
        "name": "rolling_corr",
        "description": "Returns the most recent 20-day rolling correlation between two stocks.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_a": {"type": "string"},
                "ticker_b": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker_a", "ticker_b"]
        }
    },

    {
        "name": "omega_ratio",
        "description": "Calculates the Omega ratio for a stock given a minimum acceptable return threshold.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "threshold": {
                    "type": "number",
                    "description": "Minimum acceptable return as a decimal. Defaults to 0."
                }
            },
            "required": ["ticker", "start_date", "end_date"]
        }
    },

    {
        "name": "r_squared",
        "description": "Calculates R² of a stock's returns explained by a benchmark.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "benchmark": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker", "benchmark"]
        }
    },

    {
        "name": "relative_return",
        "description": "Returns the latest-day excess return of a stock over a benchmark.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "benchmark": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["ticker", "benchmark"]
        }
    },

    {
        "name": "compare_performance",
        "description": "Compares annualized performance across multiple tickers and identifies the best performer.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols, e.g. [\"AAPL\", \"MSFT\", \"GOOG\"]."
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["tickers"]
        }
    },

    {
        "name": "compare_risk",
        "description": "Compares risk profiles (VaR + max drawdown) across multiple tickers.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["tickers"]
        }
    },

    {
        "name": "compare_volatility",
        "description": "Compares daily volatility across multiple tickers and identifies the most volatile.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["tickers"]
        }
    },

    {
        "name": "compare_relative_volatility",
        "description": "Compares relative volatility of multiple stocks against the first ticker in the list (used as reference).",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "First ticker is the reference; rest are compared against it."
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["tickers"]
        }
    },

    {
        "name": "compare_rolling_volatility",
        "description": "Compares 20-day rolling volatility across multiple tickers.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"}
            },
            "required": ["tickers"]
        }
    },

]
