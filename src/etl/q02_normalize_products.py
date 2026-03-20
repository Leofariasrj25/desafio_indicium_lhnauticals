import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Union

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read raw data from bronze layer (data/raw)
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at: {path}")

    return pd.read_csv(path)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply business rules:
    """

    df_clean = df.copy()
    initial_size = len(df_clean)

    df_clean["price"] = (
        df_clean["price"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.strip()
        .astype(float)
    )

    cat_series = df_clean["actual_category"].astype(str).str.lower()
    cat_series = cat_series.str.replace(" ", "", regex=False)
    cat_series = (
        cat_series.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    conditions = [
        cat_series.str.contains("ele", na=False),
        cat_series.str.contains("anc|enc", na=False),
        cat_series.str.contains("prop", na=False),
    ]
    choices = ["eletrônicos", "ancoragem", "propulsão"]

    df_clean["actual_category"] = np.select(conditions, choices, default="outros")
    df_clean = df_clean.drop_duplicates()

    final_size = len(df_clean)
    removed_duplicates = initial_size - final_size

    logging.info(f"Data quality: {removed_duplicates} duplicated lines were removed.")
    logging.info(f"Unique Products processed: {final_size}.")

    return df_clean


def load_data(df: pd.DataFrame, output_path: Union[str, Path]) -> None:
    """
    Saves the DataFrame in the Silver layer (data/processed/)
    Ensures the directory creation if it doesnt exist.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)


def main() -> None:
    """
    Setup the Product ETL pipeline
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    bronze_path = Path(BASE_DIR / "data" / "raw" / "produtos_raw.csv")
    silver_path = Path(BASE_DIR / "data" / "processed" / "produtos_processed.csv")

    try:
        logging.info("Initializing data extraction...")
        df_raw = extract_data(bronze_path)

        logging.info("Applying transformations...")
        df_silver = transform_data(df_raw)

        logging.info("Loading transformed data to silver layer...")
        load_data(df_silver, silver_path)

        logging.info("Product Pipeline finished successfully")
    except Exception as e:
        logging.error(f"Error while executing pipeline: {e}")
        raise


if __name__ == "__main__":
    main()
