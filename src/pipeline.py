import json
import logging
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from etl.transform_sales import transform_sales
from etl.transform_products import transform_products
from etl.transform_clients import transform_clients
from etl.transform_import_costs import transform_import_costs
from etl.transform_dolar_exchange_rates import transform_rates
from etl.build_fct_product_profitability import build_fct_product_profitability
from services.bcb_api import fetch_exchange_rates

import utils.paths as paths


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_data(file_path: Union[str, Path]):
    """
    Read raw data from bronze layer (data/raw)
    """

    path = Path(file_path)

    if file_path.name != "api" and not path.exists():
        raise FileNotFoundError(f"File not found at: {path}")

    file_name = path.name

    if file_name.endswith(".csv"):
        data = pd.read_csv(path)
    elif file_name.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif file_name.endswith("api"):
        data = fetch_exchange_rates("01-01-2023", "12-31-2024")
    else:
        raise Exception("This pipeline currently only supports .csv and .json files")

    return data


def load_data(df: pd.DataFrame, output_path: Union[str, Path]) -> None:
    """
    Saves the DataFrame in the Silver layer (data/processed/)
    Ensures the directory creation if it doesnt exist.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)


def run_etl_raw_layer(
    input_paths: dict, output_paths: dict, transformers: dict
) -> None:

    total_steps = len(input_paths)
    current_step = 1

    for file, file_path in input_paths.items():
        logging.info(f"> STEP {current_step} OF {total_steps}")
        current_step += 1

        logging.info(f"Initializing data extraction from {file_path.name}...")
        df = extract_data(file_path)

        logging.info("Applying transformations...")
        df_processed = transformers[file](df)

        logging.info("Loading transformed data to silver layer (data/processed)...")
        load_data(df_processed, output_paths[file])

        logging.info(f"{file.capitalize()} Pipeline finished successfully\n")


def main() -> None:
    """
    Setup the Product ETL pipeline
    """

    raw_paths = {
        "sales": paths.RAW_DATA_DIR / "vendas_2023_2024.csv",
        "products": paths.RAW_DATA_DIR / "produtos_raw.csv",
        "clients": paths.RAW_DATA_DIR / "clientes_crm.json",
        "import_costs": paths.RAW_DATA_DIR / "custos_importacao.json",
        "exchange_rates": Path("/api"),
    }

    processed_paths = {
        "sales": paths.PROCESSED_DATA_DIR / "vendas_2023_2024_processed.csv",
        "products": paths.PROCESSED_DATA_DIR / "produtos_processed.csv",
        "clients": paths.PROCESSED_DATA_DIR / "clientes_crm_processed.csv",
        "import_costs": paths.PROCESSED_DATA_DIR / "custos_importacao_processed.csv",
        "exchange_rates": paths.PROCESSED_DATA_DIR
        / "usdolar_exchange_rates_2023_2024.csv",
    }

    analytics_paths = {
        "profitability": paths.ANALYTICS_DATA_DIR / "fct_product_profitability.csv"
    }

    transformers = {
        "sales": transform_sales,
        "products": transform_products,
        "clients": transform_clients,
        "import_costs": transform_import_costs,
        "exchange_rates": transform_rates,
    }

    # Phase 1
    # load the different files present in data/raw
    # call the respective transformation for each file
    #  TO_DO: make api call to BCB dollar exchange rate produce a csv.
    # Phase 2 - Analytics
    try:
        logging.info("--- PHASE 1: Raw to Processed (Silver Layer) ---")
        run_etl_raw_layer(
            input_paths=raw_paths,
            output_paths=processed_paths,
            transformers=transformers,
        )

        logging.info("--- PHASE 2: Processed to Analytics (Gold Layer) ---")
        build_fct_product_profitability(
            sales_path=processed_paths["sales"],
            import_costs_path=processed_paths["import_costs"],
            usdolar_exchange_rates_path=processed_paths["exchange_rates"],
            output_path=analytics_paths["profitability"],
        )
    except Exception as e:
        logging.error(f"Error while executing pipeline: {e}")
        raise


if __name__ == "__main__":
    main()
