import json
import pandas as pd
import logging
from pathlib import Path
from typing import Union


def organize_columns(row):
    val0 = str(row[0]).strip()
    val1 = str(row[1]).strip()

    if len(val0) == 2:
        return pd.Series([val0, val1])
    else:
        return pd.Series([val1, val0])


def transform_clients(raw_json: Union[dict, list]) -> pd.DataFrame:
    """
    Apply business rules:
        - rename code to client id
        - clean and normalize email
        - order the columns: client_id, full_name, location, email
        - extract state and municipality from location into their own columns
    """

    df_flattened = pd.json_normalize(raw_json)
    df_flattened = df_flattened.rename(columns={"code": "client_id"})

    column_names = ["client_id", "full_name", "location", "email"]
    df_flattened = df_flattened.reindex(columns=column_names)

    df_email_normalized = df_flattened
    count = df_flattened["email"].str.contains("#", na=False).sum()
    logging.info(f"Fixing the formatting of {count} emails...")
    df_email_normalized["email"] = df_flattened["email"].str.replace("#", "@")

    df_split = df_email_normalized["location"].str.split(
        r"\s*[/,-]\s*", n=1, expand=True
    )

    df_email_normalized[["state", "municipality"]] = df_split.apply(
        organize_columns, axis=1
    )

    final_columns = ["client_id", "full_name", "email", "state", "municipality"]
    df_final = df_email_normalized[final_columns]
    df_final = df_final.drop_duplicates()  # sanity check

    municipality_count = df_final["municipality"].nunique()
    state_count = df_final["state"].nunique()
    logging.info(
        f"Identified clients in {state_count} states, across {municipality_count} municipalities"
    )
    logging.info(f"{len(df_final)} clients processed.")

    return df_final
