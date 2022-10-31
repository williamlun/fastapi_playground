"""Network Server RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic


class NetworkServer(pydantic.BaseModel):
    id: str
    name: str
    server: str
