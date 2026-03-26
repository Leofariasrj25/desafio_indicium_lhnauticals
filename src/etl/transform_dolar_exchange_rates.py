import pandas as pd


def transform_rates(raw_json) -> pd.DataFrame:
    df_rates = pd.DataFrame(raw_json)
    df_rates["dataHoraCotacao"] = pd.to_datetime(df_rates["dataHoraCotacao"]).dt.date
    df_rates.rename(
        columns={"cotacaoVenda": "usd_rate", "dataHoraCotacao": "rate_date"},
        inplace=True,
    )

    return df_rates
