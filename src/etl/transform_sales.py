import pandas as pd


def transform_sales(df_raw_sales: pd.DataFrame) -> pd.DataFrame:
    df_sales_normalized = df_raw_sales.drop_duplicates()

    df_sales_normalized["sale_date"] = pd.to_datetime(
        df_sales_normalized["sale_date"], format="mixed"
    )

    df_sales_normalized["sale_date"] = df_sales_normalized["sale_date"].dt.strftime(
        "%Y-%m-%d"
    )

    df_sales_normalized = df_sales_normalized.sort_values(
        by=["sale_date", "id"], ascending=[True, True]
    )

    df_sales_normalized["id"] = range(1, len(df_sales_normalized) + 1)
    df_sales_normalized = df_sales_normalized.reset_index(drop=True)

    return df_sales_normalized
