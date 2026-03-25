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


def extract_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read raw data from bronze layer (data/raw)
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_data(raw_json: Union[dict, list]) -> pd.DataFrame:
    df_flattened = pd.json_normalize(raw_json)
    df_flattened = df_flattened.rename(columns={"code": "client_id"})

    column_names = ["client_id", "full_name", "location", "email"]
    df_flattened = df_flattened.reindex(columns=column_names)

    df_email_normalized = df_flattened
    df_email_normalized["email"] = df_flattened["email"].str.replace("#", "@")

    print(df_email_normalized.head(5))

    # TO-DO: split location into two columns (State, City)


def main() -> None:
    file_path = Path(Path.cwd()) / "data" / "raw" / "clientes_crm.json"

    transform_data(extract_data(file_path))


if __name__ == "__main__":
    main()

