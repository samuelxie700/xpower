from __future__ import annotations
import math
from pathlib import Path
import pandas as pd


def load_usage_table(file_or_obj) -> pd.DataFrame:
    if file_or_obj is None or isinstance(file_or_obj, bool):
        raise TypeError("file_or_obj must be a valid path or file-like")
    try:
        df = pd.read_csv(file_or_obj)
    except Exception as e:
        raise ValueError(f"CSV read failed: {e}")
    df.rename(columns={c: c.strip().lower() for c in df.columns}, inplace=True)
    if "kwh" not in df.columns:
        raise ValueError("missing kWh column")
    df.rename(columns={"kwh": "kWh"}, inplace=True)
    df["kWh"] = pd.to_numeric(df["kWh"], errors="coerce")
    df = df.dropna(subset=["kWh"])
    if df.empty:
        raise ValueError("no valid kWh data")
    return df


def sum_usage_kwh(df: pd.DataFrame, col: str = "kWh") -> float:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if col not in df.columns:
        raise ValueError(f"missing column: {col}")
    if (df[col] < 0).any():
        raise ValueError("negative values found")
    total = float(df[col].sum())
    if not math.isfinite(total):
        raise ValueError("total is not finite")
    return round(total, 6)


def assert_inputs_ok(total_usage, rate, fixed_fee) -> None:
    for name, v in (("total_usage", total_usage), ("rate", rate), ("fixed_fee", fixed_fee)):
        if v is None or isinstance(v, bool):
            raise TypeError(f"{name} cannot be None or bool")
        if not isinstance(v, (int, float)):
            raise TypeError(f"{name} must be numeric")
        f = float(v)
        if not math.isfinite(f):
            raise ValueError(f"{name} must be finite")
        if f < 0:
            raise ValueError(f"{name} must be >= 0")


def fixed_rate_bill(total_usage: float, rate: float, fixed_fee: float, *, rounding: int = 2) -> float:
    assert_inputs_ok(total_usage, rate, fixed_fee)
    amount = float(total_usage) * float(rate) + float(fixed_fee)
    if isinstance(rounding, int) and rounding >= 0:
        return round(amount, rounding)
    return float(amount)


def main():
    file_path = Path("sample_usage_data_month.csv")
    rate = 0.25
    fixed_fee = 10.0
    df = load_usage_table(file_path)
    total = sum_usage_kwh(df, "kWh")
    bill = fixed_rate_bill(total, rate, fixed_fee)
    print("===== Fixed-Rate Bill =====")
    print("Total electricity consumption:", total, "kWh")
    print("Rate: $", rate, "/kWh")
    print("Fixed fee: $", fixed_fee)
    print("Bill Amount: $", bill)


if __name__ == "__main__":  # pragma: no cover
    main()
