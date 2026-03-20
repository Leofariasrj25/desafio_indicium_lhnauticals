import sys
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from src.etl import q02_normalize_products
from src.etl import q03_flatten_imports

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ETL_DIR = BASE_DIR / "src" / "etl"
sys.path.append(str(ETL_DIR))


ETL_DEPENDENCY_MAP = {
    "produtos_processed.csv": q02_normalize_products.main,
    "custos_importacao_processed.csv": q03_flatten_imports.main,
}


def load_datasets(
    file_names: list[str], layer: str = "processed"
) -> Dict[str, pd.DataFrame]:
    """
    Loads requested datasets into a dictionary. Triggers ETL if processed files are missing.
    """

    dataframes = {}
    target_dir = BASE_DIR / "data" / layer

    for file_name in file_names:
        file_path = target_dir / file_name

        if layer == "processed" and not file_path.exists():
            logging.warning(f"Missing {file_name}. Triggering ETL pipeline...")
            etl_function = ETL_DEPENDENCY_MAP.get(file_name)

            if etl_function:
                etl_function()
            else:
                raise FileNotFoundError(f"No ETL mapping found to generate {file_name}")

        if not file_path.exists():
            raise FileNotFoundError(
                f"Critical error: {file_path} does not exist even after ETL attempt."
            )

        dataframes[file_name] = pd.read_csv(file_path)

    return dataframes
