import pandas as pd
import json
import logging
from pathlib import Path
from typing import Union

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_data(file_path: Union[Path, str]) -> Union[dict, list]:
    """
    Reads the raw JSON data from Bronze layer (data/raw).
    json.load is used to preserve the hierarchical structure in memory.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_data(raw_json: Union[dict, list]) -> pd.DataFrame:
    """
    Flattens JSON's hierarchical structure to a tabular format and
    applies rigorous typing required by the database
    """
    df_flattened = pd.json_normalize(
        data=raw_json,
        record_path="historic_data",
        meta=["product_id", "product_name", "category"],
    )

    line_count = len(df_flattened)
    ordered_columns = [
        "product_id",
        "product_name",
        "category",
        "start_date",
        "usd_price",
    ]
    df_flattened = df_flattened[ordered_columns]

    df_flattened["start_date"] = pd.to_datetime(
        df_flattened["start_date"], format="%d/%m/%Y"
    )

    df_flattened["usd_price"] = df_flattened["usd_price"].astype(float)

    logging.info(f"JSON flattened successfully. Total extracted records: {line_count}")

    return df_flattened


def load_data(df: pd.DataFrame, output_path: Union[Path, str]) -> None:
    """
    Saves the DataFrame to the Silver layer (data/processed/)
    Ensures the directory creation if it doesnt exist.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)


def main() -> None:
    """
    Orchestrates the Importing Costs ETL pipeline.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    bronze_path = BASE_DIR / "data" / "raw" / "custos_importacao.json"
    silver_path = BASE_DIR / "data" / "processed" / "custos_importacao_processed.csv"

    try:
        logging.info("Initializing data extraction (JSON)...")
        raw_data = extract_data(bronze_path)

        logging.info("Flattening...")
        df_silver = transform_data(raw_data)

        logging.info("Loading tabular data to Silver layer...")
        load_data(df_silver, silver_path)

        logging.info("Importing Costs Pipeline finished successfully.")
    except Exception as e:
        logging.error(f"Error while executing pipeline: {e}")
        raise


if __name__ == "__main__":
    main()
