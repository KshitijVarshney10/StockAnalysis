# MarketMind — AI Equity Research Terminal

A conversational stock analysis assistant powered by GPT function-calling and `yfinance`.
Ask questions in plain English; MarketMind routes them to the right financial computation automatically.

## What You Can Ask

| Category | Example queries |
|---|---|
| Price | `What's the current price of AAPL?` |
| Charts | `Plot NVDA price for last year` |
| Indicators | `RSI for TSLA` · `MACD for MSFT` |
| Moving Avg | `50-day SMA for AMZN` |
| Risk | `Max drawdown of COIN since 2023-01-01` |
| Sharpe | `Sharpe ratio for SPY from 2022-01-01 to 2023-01-01` |
| Volatility | `Rolling volatility chart for META` |
| Comparison | `Compare AAPL vs MSFT vs GOOG performance` |
| Correlation | `Beta of TSLA vs SPY` |

## Project Structure

MarketMind/
├── app.py            # Streamlit UI + GPT orchestration
├── analytics.py      # All financial computation functions
├── tool_schemas.py   # OpenAI function-calling schemas
├── requirements.txt
└── .env.example