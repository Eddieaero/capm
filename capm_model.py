import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import datetime
from typing import Optional, Dict, Any


def calculate_capm(
    ticker: str,
    benchmark: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    risk_free_rate: float,
    annualization: int = 252,
    use_log_returns: bool = False,
    annualization_method: str = "arithmetic",
    verbose: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Returns a dictionary with keys:
      - expected_return: float (annualized)
      - beta: float
      - alpha: float (regression intercept)
      - beta_stderr: float or None
      - r_squared: float
      - market_annual_return: float
      - market_risk_premium: float
      - n_obs: int

    If there is an error (insufficient data, zero variance, download failure),
    returns None.

    Args:
        ticker: Stock ticker symbol
        benchmark: Market benchmark ticker
        start_date: Start of historical period
        end_date: End of historical period
        risk_free_rate: Annual risk-free rate as decimal (e.g., 0.04 for 4%)
        annualization: Trading days per year (default: 252)
        use_log_returns: Use log returns instead of simple returns
        annualization_method: Either "arithmetic" or "geometric" for market return
        verbose: Print detailed analysis
    """
    if annualization_method not in ["arithmetic", "geometric"]:
        if verbose:
            print(f"Invalid annualization_method: {annualization_method}. Using 'arithmetic'.")
        annualization_method = "arithmetic"

    if verbose:
        print(f"Fetching data for {ticker} and {benchmark} from {start_date.date()} to {end_date.date()}...")

    try:
        raw = yf.download([ticker, benchmark], start=start_date, end=end_date)
    except Exception as e:
        if verbose:
            print(f"Error downloading data: {e}")
        return None

    if raw is None or getattr(raw, "empty", True):
        if verbose:
            print("No data returned from source.")
        return None

    # Helper: extract adjusted close prices robustly from yfinance output
    def _extract_adj_close(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        if df is None or getattr(df, "empty", True):
            return None

        # If a Series was returned (single ticker result), convert to DataFrame
        if isinstance(df, pd.Series):
            name = df.name if df.name is not None else ticker
            return df.to_frame(name=name)

        # If DataFrame has MultiIndex columns (typical yfinance when downloading multiple fields)
        if isinstance(df.columns, pd.MultiIndex):
            # Common layout: level 0 contains fields like 'Adj Close'
            if "Adj Close" in df.columns.levels[0]:
                return df["Adj Close"]

            # Try to find any level that looks like adjusted close
            for lvl in range(df.columns.nlevels):
                vals = df.columns.get_level_values(lvl).unique()
                for v in vals:
                    if isinstance(v, str) and ("Adj" in v or "Close" in v):
                        try:
                            extracted = df.xs(v, axis=1, level=lvl)
                            # ensure we have two columns (tickers) or more
                            if not getattr(extracted, "empty", False):
                                return extracted
                        except Exception:
                            continue

            # Fallback: attempt to flatten and pick columns that match tickers
            flat = df.copy()
            flat.columns = ["_".join(map(str, c)).strip() for c in flat.columns.values]
            # If tickers are present as substrings in flattened names, try to select them
            cols = [c for c in flat.columns if any(sym in c for sym in (ticker, benchmark))]
            if cols:
                return flat[cols]

            return None

        # If DataFrame has single-level columns
        if "Adj Close" in df.columns:
            return df["Adj Close"]

        # Otherwise assume the DataFrame already contains price series with tickers as columns
        return df

    data = _extract_adj_close(raw)

    if data is None or getattr(data, "empty", True):
        if verbose:
            print("Failed to extract adjusted close prices from yfinance result.")
        return None

    # Align and drop NaNs to ensure same-date observations
    data = data.dropna(how="any")

    if data.shape[0] < 2:
        if verbose:
            print("Not enough data after alignment to compute returns.")
        return None

    # Compute returns
    if use_log_returns:
        returns = np.log(data / data.shift(1)).dropna()
    else:
        returns = data.pct_change().dropna()

    if returns.empty:
        if verbose:
            print("No returns available after pct_change/log-return computation.")
        return None

    # Extract series
    try:
        stock_returns = returns[ticker]
        market_returns = returns[benchmark]
    except KeyError as e:
        if verbose:
            print(f"Ticker missing in downloaded data: {e}")
        return None

    n_obs = len(stock_returns)
    if n_obs < 2:
        if verbose:
            print("Insufficient observations for regression.")
        return None

    # Check market variance
    if market_returns.var() == 0:
        if verbose:
            print("Market returns variance is zero; cannot compute beta.")
        return None

    # Use linear regression to estimate beta (slope)
    lr = stats.linregress(market_returns, stock_returns)
    beta = lr.slope
    alpha = lr.intercept
    beta_stderr = lr.stderr
    r_squared = lr.rvalue ** 2

    # Compute market return (arithmetic or geometric annualization)
    if annualization_method == "geometric":
        if use_log_returns:
            # For log returns: exp(mean(log_ret) * 252) - 1
            market_annual_return = np.exp(market_returns.mean() * annualization) - 1
        else:
            # For simple returns: (1 + mean(ret))^252 - 1
            market_annual_return = (1 + market_returns.mean()) ** annualization - 1
    else:  # arithmetic
        if use_log_returns:
            # Convert log returns to simple returns for arithmetic scaling
            market_annual_return = (np.exp(market_returns.mean()) - 1) * annualization
        else:
            # Simple multiplication for arithmetic mean
            market_annual_return = market_returns.mean() * annualization

    market_risk_premium = market_annual_return - risk_free_rate
    expected_return = risk_free_rate + beta * market_risk_premium

    result = {
        "expected_return": expected_return,
        "beta": beta,
        "alpha": alpha,
        "beta_stderr": beta_stderr,
        "r_squared": r_squared,
        "market_annual_return": market_annual_return,
        "market_risk_premium": market_risk_premium,
        "n_obs": n_obs,
    }

    if verbose:
        print("\n--- CAPM Analysis Results ---")
        print(f"Stock Ticker: {ticker}")
        print(f"Benchmark Ticker: {benchmark}")
        print("-" * 30)
        print(f"Risk-Free Rate (Rf): {risk_free_rate:.4f} ({risk_free_rate:.2%})")
        print(f"Annualized Market Return (E(Rm)): {market_annual_return:.4f} ({market_annual_return:.2%})")
        print(f"Market Risk Premium (MRP): {market_risk_premium:.4f} ({market_risk_premium:.2%})")
        print(f"Calculated Beta (β): {beta:.4f}")
        print(f"Alpha (α): {alpha:.6f}")
        if beta_stderr is not None:
            print(f"Beta StdErr: {beta_stderr:.6f}")
        print(f"R-squared: {r_squared:.4f}")
        print("-" * 30)
        print(f"Required Expected Return (Cost of Equity): {expected_return:.4f} ({expected_return:.2%})")

    return result

if __name__ == "__main__":
    # --- Main Execution Block ---
    # Define the parameters for the CAPM model
    STOCK_TICKER = "MSFT"  # Microsoft as example
    MARKET_BENCHMARK = "^GSPC"  # S&P 500 Index
    # Use a 2-year period ending today
    END = datetime.datetime.now()
    START = END - datetime.timedelta(days=2*365)
    # Use a current estimate for the 10-year Treasury yield (annual decimal)
    RISK_FREE = 0.04

    result = calculate_capm(
        STOCK_TICKER,
        MARKET_BENCHMARK,
        START,
        END,
        RISK_FREE,
        annualization=252,
        use_log_returns=False,
        annualization_method="geometric",  # Try geometric compounding
        verbose=True,
    )

    if result is None:
        print("\nCAPM calculation failed.")
    else:
        er = result.get("expected_return")
        beta = result.get("beta")
        alpha = result.get("alpha", 0)
        rsq = result.get("r_squared", 0)
        print("\nCAPM Model Summary:")
        print(f"Expected Return (annual): {er:.4f} ({er:.2%})")
        print(f"Beta: {beta:.4f}, Alpha: {alpha:.6f}, R²: {rsq:.4f}")