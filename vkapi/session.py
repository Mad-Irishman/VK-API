import typing as tp
import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from urllib3.util import Retry


class Session:
    """
    Сессия.

    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        retry_strat = Retry(
            total=max_retries, backoff_factor=backoff_factor, status_forcelist=[
                429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strat)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url: str, **kwargs: tp.Any) -> requests.Response:
        response = self.session.get(
            url=f"{self.base_url}/{url}", timeout=kwargs.get("timeout", self.timeout)
        )
        return response

    def post(self, url: str, **kwargs: tp.Any) -> requests.Response:
        response = self.session.post(
            url=f"{self.base_url}/{url}", timeout=kwargs.get("timeout", self.timeout), data=kwargs
        )
        return response
