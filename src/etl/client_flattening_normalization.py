# load the client data
# apply transformations
#   1. flatten the json file(done)
#   2. replace '#' with proper @ on emails.
#   3. normalize columns
#   4. normalize location

import json
import pandas as pd
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

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def organize_columns(row):
    val0 = str(row[0]).strip()
    val1 = str(row[1]).strip()

    if len(val0) == 2:
        return pd.Series([val0, val1])
    else:
        return pd.Series([val1, val0])


def transform_data(raw_json: Union[dict, list]) -> pd.DataFrame:
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


def load_data(df_clients: pd.DataFrame, output_path: Union[str, Path]) -> None:
    """
    Saves the DataFrame in the Silver layer (data/processed/)
    Ensures the directory creation if it doesn't exist.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df_clients.to_csv(path, index=False)


def main() -> None:
    """
    Setup the Client ETL pipeline
    """

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    input_path = BASE_DIR / "data" / "raw" / "clientes_crm.json"
    output_path = BASE_DIR / "data" / "processed" / "clientes_crm_processed.csv"

    try:
        logging.info("Initializing data extraction...")
        raw_json = extract_data(input_path)

        logging.info("Applying transformations...")
        df_clients = transform_data(raw_json)

        logging.info("Loading transformed data to silver layer...")
        load_data(df_clients, output_path)

        logging.info("Client Pipeline finished successfully")
    except Exception as e:
        logging.error(f"Error while executing pipeline: {e}")


if __name__ == "__main__":
    main()
