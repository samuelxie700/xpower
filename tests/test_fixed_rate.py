import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
from fixed_rate import load_usage_table, sum_usage_kwh, assert_inputs_ok, fixed_rate_bill, main


def test_invalid_cases(tmp_path):
    # load_usage_table
    with pytest.raises(ValueError):
        load_usage_table("not_exist.csv")
    with pytest.raises(TypeError):
        load_usage_table(None)
    with pytest.raises(TypeError):
        load_usage_table(True)
    p = tmp_path / "bad.csv"
    p.write_text("val\n100\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_usage_table(p)  # missing kWh column
    p2 = tmp_path / "nan.csv"
    p2.write_text("kWh\nx\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_usage_table(p2)

    # sum_usage_kwh
    with pytest.raises(ValueError):
        sum_usage_kwh(pd.DataFrame({"kWh": [1.0, -0.5]}))
    with pytest.raises(TypeError):
        sum_usage_kwh("not_a_df")
    df_inf = pd.DataFrame({"kWh": [float("inf")]})
    with pytest.raises(ValueError):
        sum_usage_kwh(df_inf)  # total not finite
    df_no_col = pd.DataFrame({"x": [1.0, 2.0]})
    with pytest.raises(ValueError):
        sum_usage_kwh(df_no_col)  # missing column (line 29)

    # assert_inputs_ok
    with pytest.raises(TypeError):
        assert_inputs_ok(None, 0.25, 10)
    with pytest.raises(ValueError):
        assert_inputs_ok(float("inf"), 0.25, 10)

    # fixed_rate_bill
    with pytest.raises(ValueError):
        fixed_rate_bill(-1, 0.25, 10)
    with pytest.raises(TypeError):
        fixed_rate_bill("100", 0.25, 10)



def test_typical_cases(tmp_path):
    # load_usage_table + sum_usage_kwh
    p = tmp_path / "ok.csv"
    p.write_text("kWh\n1.2\n0.8\n", encoding="utf-8")
    df = load_usage_table(p)
    assert sum_usage_kwh(df) == 2.0

    # assert_inputs_ok
    assert_inputs_ok(100, 0.25, 10)

    # fixed_rate_bill
    assert fixed_rate_bill(300, 0.25, 10) == 85.0
    assert fixed_rate_bill(200, 0.20, 0) == 40.0


def test_boundary_cases(monkeypatch, capsys):
    # fixed_rate_bill boundaries
    assert fixed_rate_bill(0, 0.25, 10) == 10
    assert fixed_rate_bill(500, 0, 50) == 50
    assert fixed_rate_bill(1000, 0.25, 0) == 250
    assert fixed_rate_bill(100, 0.25, 10, rounding=-1) == 35.0

    # sum_usage_kwh large number
    df_large = pd.DataFrame({"kWh": [1_000_000]})
    assert sum_usage_kwh(df_large) == 1_000_000.0

    # assert_inputs_ok edge values
    assert_inputs_ok(0, 0, 0)

    # main smoke test
    fake_df = pd.DataFrame({"kWh": [1.0, 2.0, 3.0]})
    monkeypatch.setattr("fixed_rate.load_usage_table", lambda _: fake_df)
    monkeypatch.setattr("fixed_rate.sum_usage_kwh", lambda df, col="kWh": 6.0)
    main()
    out = capsys.readouterr().out
    assert "11.5" in out
