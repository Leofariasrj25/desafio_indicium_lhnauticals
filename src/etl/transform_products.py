import pandas as pd
import numpy as np
import logging


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
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
