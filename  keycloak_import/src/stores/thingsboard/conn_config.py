"""Thingsboard Connection Init"""
from typing import Optional
import requests


class ConnectionConfig:
    """Implementation of ConnectionConfig"""

    _instance: Optional["ConnectionConfig"] = None

    def __init__(
        self,
        host: str,
        port: int,
        username: str = "tenant@thingsboard.org",
        password: str = "tenant",
    ) -> None:
        if ConnectionConfig._instance is not None:
            raise Exception("This class is a singleton")

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

    def get_url(self, resource: str) -> str:
        return f"http://{self._host}:{self._port}/api/{resource}"

    def get_token(self) -> str:
        login_url = self.get_url("auth/login")
        req_body = {"username": self._username, "password": self._password}
        jwt_response = requests.post(login_url, json=req_body).json()
        return jwt_response["token"]
