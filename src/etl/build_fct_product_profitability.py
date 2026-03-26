import logging
from pathlib import Path
from typing import Union

import pandas as pd
import numpy as np

import utils.paths as paths


def process_profitability(
    df_sales: pd.DataFrame, df_costs: pd.DataFrame, df_rates: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich sales data with historical exchange rates and unit costs.
    """
    df_sales["sale_date"] = pd.to_datetime(
        df_sales["sale_date"], format="mixed", dayfirst=True
    )
    df_costs["start_date"] = pd.to_datetime(df_costs["start_date"])
    df_rates["rate_date"] = pd.to_datetime(df_rates["rate_date"])

    df_sales = df_sales.sort_values("sale_date")
    df_costs = df_costs.sort_values("start_date")
    df_rates = df_rates.sort_values("rate_date")

    df_enriched = pd.merge_asof(
        df_sales,
        df_rates,
        left_on="sale_date",
        right_on="rate_date",
        direction="backward",
    )

    df_final = pd.merge_asof(
        df_enriched,
        df_costs,
        left_on="sale_date",
        right_on="start_date",
        left_by="id_product",
        right_by="product_id",
        direction="backward",
    )

    return df_final


def calculate_financials(df_final: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate transaction costs, identify losses, and aggregate metrics by product.
    """
    df_final["unit_cost_brl"] = df_final["usd_price"] * df_final["usd_rate"]
    df_final["total_cost_brl"] = df_final["unit_cost_brl"] * df_final["qtd"]

    df_final["profit_brl"] = df_final["total"] - df_final["total_cost_brl"]
    df_final["loss_amount"] = np.where(
        df_final["profit_brl"] < 0, abs(df_final["profit_brl"]), 0.0
    )

    df_agg = (
        df_final.groupby("id_product")
        .agg(total_revenue=("total", "sum"), total_loss=("loss_amount", "sum"))
        .reset_index()
    )

    df_agg["loss_percentage"] = (df_agg["total_loss"] / df_agg["total_revenue"]).fillna(
        0.0
    )

    df_agg["total_revenue"] = df_agg["total_revenue"].round(2)
    df_agg["total_loss"] = df_agg["total_loss"].round(2)
    df_agg["loss_percentage"] = df_agg["loss_percentage"].round(4)

    return df_agg


def build_fct_product_profitability(
    sales_path: Union[str, Path],
    import_costs_path: Union[str, Path],
    usdolar_exchange_rates_path: Union[str, Path],
    output_path: Union[str, Path],
) -> None:
    """
    Orchestrate the profitability ETL pipeline.
    """

    try:
        logging.info("Loading local datasets...")
        df_sales = pd.read_csv(sales_path)
        df_costs = pd.read_csv(import_costs_path)
        df_rates = pd.read_csv(usdolar_exchange_rates_path)

        logging.info("Applying Time-Series AsOf Joins (Sales, Costs, Rates)...")
        df_enriched = process_profitability(df_sales, df_costs, df_rates)

        logging.info("Calculating financial models...")
        df_financials = calculate_financials(df_enriched)

        if isinstance(output_path, str):
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_financials.to_csv(output_path, index=False)

    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}")
        raise
