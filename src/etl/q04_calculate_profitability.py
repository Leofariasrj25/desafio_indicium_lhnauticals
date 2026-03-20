import logging
from pathlib import Path

import pandas as pd
import numpy as np
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_exchange_rate(start_date: str, end_date: str) -> list:
    """
    Fetch historical USD to BRL exchange rates from the BCB API.
    """
    url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"

    params = {
        "@dataInicial": f"'{start_date}'",
        "@dataFinalCotacao": f"'{end_date}'",
        "$format": "json",
        "$select": "cotacaoVenda,dataHoraCotacao",
    }

    logging.info(f"Fetching BCB exchange rates from {start_date} to {end_date}...")
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json().get("value", [])


def transform_exchange_rate(raw_data: list) -> pd.DataFrame:
    """
    Transform the raw API response into a typed and sorted DataFrame.
    """
    if not raw_data:
        raise ValueError("Central Bank's API did not return data for this period.")

    df_exchange_rate = pd.DataFrame(raw_data)
    df_exchange_rate["dataHoraCotacao"] = pd.to_datetime(
        df_exchange_rate["dataHoraCotacao"]
    ).dt.normalize()

    df_exchange_rate = df_exchange_rate.rename(
        columns={"dataHoraCotacao": "exchange_date", "cotacaoVenda": "selling_rate"}
    )

    df_exchange_rate = df_exchange_rate.sort_values("exchange_date").reset_index(
        drop=True
    )

    logging.info(
        f"Exchange rates extracted successfully. Mapped business days: {len(df_exchange_rate)}"
    )

    return df_exchange_rate


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

    df_sales = df_sales.sort_values("sale_date")
    df_costs = df_costs.sort_values("start_date")
    df_rates = df_rates.sort_values("exchange_date")

    df_enriched = pd.merge_asof(
        df_sales,
        df_rates,
        left_on="sale_date",
        right_on="exchange_date",
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
    df_final["unit_cost_brl"] = df_final["usd_price"] * df_final["selling_rate"]
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


def main() -> None:
    """
    Orchestrate the profitability ETL pipeline.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent

    sales_path = BASE_DIR / "data" / "raw" / "vendas_2023_2024.csv"
    costs_path = BASE_DIR / "data" / "processed" / "custos_importacao_processed.csv"
    output_path = BASE_DIR / "data" / "processed" / "fct_product_profitability.csv"

    try:
        logging.info("Loading local datasets...")
        df_vendas = pd.read_csv(sales_path)
        df_custos = pd.read_csv(costs_path)

        logging.info("Accessing Central Bank API...")
        raw_rates = extract_exchange_rate("01-01-2023", "12-31-2024")
        df_rates = transform_exchange_rate(raw_rates)

        logging.info("Applying Time-Series AsOf Joins (Sales, Costs, Rates)...")
        df_enriched = process_profitability(df_vendas, df_custos, df_rates)

        logging.info("Calculating financial models...")
        df_financials = calculate_financials(df_enriched)

        logging.info("Saving aggregated report to Silver layer...")
        df_financials.to_csv(output_path, index=False)
        logging.info(f"Pipeline finished.")

    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
