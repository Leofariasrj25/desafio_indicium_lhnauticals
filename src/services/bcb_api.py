import pandas as pd
import requests


def fetch_exchange_rates(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetches USD/BRL rates from BCB API and returns a DataFrame."""

    url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    params = {
        "@dataInicial": f"'{start_date}'",
        "@dataFinalCotacao": f"'{end_date}'",
        "$format": "json",
        "$select": "cotacaoVenda,dataHoraCotacao",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json().get("value", [])
