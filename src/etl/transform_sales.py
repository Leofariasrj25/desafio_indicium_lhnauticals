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

    return pd.open_csv(file_path)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
