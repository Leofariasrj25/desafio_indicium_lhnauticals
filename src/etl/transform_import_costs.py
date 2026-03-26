import logging
from typing import Union

import pandas as pd


def transform_import_costs(raw_json: Union[dict, list]) -> pd.DataFrame:
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
