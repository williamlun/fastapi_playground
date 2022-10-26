from typing import Optional
import requests
from loguru import logger


class ConnectionConfig:

    _instance: Optional["ConnectionConfig"] = None

    def __init__(self, host: str, port: int, username: str, password: str):
        if ConnectionConfig._instance is not None:
            raise Exception("This class is a singleton!")

        self._host = host
        self._port = port
        self._username = username
        self._password = password

        ConnectionConfig._instance = self

    @staticmethod
    def get_instance() -> "ConnectionConfig":
        if ConnectionConfig._instance is None:
            raise Exception("ConnectionConfig is not initialized!")
        return ConnectionConfig._instance

    def get_url(self, suffix: str) -> str:
        return f"http://{self._host}:{self._port}/admin/realms/{suffix}"

    def get_token(self) -> str:
        login_url = f"http://{self._host}:{self._port}/realms/master/protocol/openid-connect/token"
        logger.info(login_url)
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = f"client_id=admin-cli&grant_type=password&username={self._username}&password={self._password}"

        token_response = requests.post(login_url, headers=header, data=payload).json()
        logger.info(token_response)
        return token_response["access_token"]
