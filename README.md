# CAPM Model Calculator

A Python implementation of the Capital Asset Pricing Model (CAPM) that calculates the expected return (cost of equity) for stocks using historical price data from Yahoo Finance.

## Features

- Fetches historical adjusted close prices using `yfinance`
- Calculates beta using regression analysis
- Supports both arithmetic and geometric return annualization
- Options for log or simple returns
- Robust handling of various data formats and market conditions
- Detailed statistical outputs (beta, alpha, R-squared)

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Quick Start

```python
import datetime
from capm_model import calculate_capm

# Example: Calculate CAPM for Microsoft vs S&P 500
result = calculate_capm(
    ticker="MSFT",
    benchmark="^GSPC",  # S&P 500
    start_date=datetime.datetime(2023, 1, 1),
    end_date=datetime.datetime.now(),
    risk_free_rate=0.04,  # 4% annual rate
    annualization_method="geometric",
    verbose=True
)

if result:
    print(f"Expected Return: {result['expected_return']:.2%}")
    print(f"Beta: {result['beta']:.4f}")
    print(f"Alpha: {result['alpha']:.6f}")
```

## API Reference

### `calculate_capm()`

```python
def calculate_capm(
    ticker: str,
    benchmark: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    risk_free_rate: float,
    annualization: int = 252,
    use_log_returns: bool = False,
    annualization_method: str = "arithmetic",
    verbose: bool = True
) -> Optional[Dict[str, Any]]
```

#### Parameters

- `ticker`: Stock ticker symbol (e.g., "AAPL", "MSFT")
- `benchmark`: Market benchmark ticker (e.g., "^GSPC" for S&P 500)
- `start_date`: Start date for historical data
- `end_date`: End date for historical data
- `risk_free_rate`: Annual risk-free rate as decimal (e.g., 0.04 for 4%)
- `annualization`: Trading days per year (default: 252)
- `use_log_returns`: Use logarithmic returns instead of simple returns
- `annualization_method`: "arithmetic" or "geometric" for return annualization
- `verbose`: Print detailed analysis results

#### Returns

Dictionary with the following keys:
- `expected_return`: Annualized expected return (decimal)
- `beta`: Stock's beta coefficient
- `alpha`: Regression intercept (Jensen's alpha)
- `beta_stderr`: Standard error of beta estimate
- `r_squared`: R-squared of the regression
- `market_annual_return`: Annualized market return
- `market_risk_premium`: Market risk premium (Rm - Rf)
- `n_obs`: Number of observations used

Returns `None` if there's insufficient data or an error occurs.

## Mathematical Details

The CAPM formula used is:

E(Ri) = Rf + β * (E(Rm) - Rf)

Where:
- E(Ri) is the expected return of the stock
- Rf is the risk-free rate
- β (beta) is calculated using regression of stock returns on market returns
- E(Rm) is the expected market return
- (E(Rm) - Rf) is the market risk premium

Beta is estimated using linear regression of stock returns against market returns. The implementation supports both:
- Simple returns: (P₁ - P₀) / P₀
- Log returns: ln(P₁/P₀)

And two annualization methods:
- Arithmetic: r_annual = r_daily * 252
- Geometric: r_annual = (1 + r_daily)^252 - 1

## Dependencies

- yfinance: Download historical market data
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- scipy: Statistical functions (linear regression)

## Error Handling

The implementation includes robust error handling for:
- Missing or insufficient data
- Zero variance in market returns
- Data download failures
- Various Yahoo Finance API return formats

## License

MIT License - feel free to use, modify, and distribute.