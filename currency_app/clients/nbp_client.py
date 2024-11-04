from typing import Any

import furl
from requests import Session

from currency_app.settings import settings


class NBPClient:
    def __init__(self):
        self._url = furl.furl(settings.nbp_api_url)
        self._url.args["format"] = "json"
        self._session: Session = Session()

    def get_currency_rate(self, currency: str) -> float:
        rates = self._get_rates()
        return self._find_currency_by_rate(rates, currency)

    def _get_rates(self) -> list[dict[str, Any]]:
        response = self._session.get(self._url.url)
        response.raise_for_status()
        table_a = response.json()[0]
        return table_a["rates"]

    @staticmethod
    def _find_currency_by_rate(rates: list[dict[str, Any]], currency: str) -> float:
        for rate in rates:
            if rate["code"] == currency:
                return rate["mid"]
        raise ValueError(f"Currency {currency} not found in rates")
