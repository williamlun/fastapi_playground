import pydantic
import requests


class Customer(pydantic.BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    email_: pydantic.EmailStr = "123"


def main():

    _req_header = {
        "accept": "application/json",
        "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzeXNhZG1pbkB0aGluZ3Nib2FyZC5vcmciLCJzY29wZXMiOlsiU1lTX0FETUlOIl0sInVzZXJJZCI6IjRmYmQ0ZjEwLTc2ZGQtMTFlZC04ZTJmLTdiZjE0NTRiZTJhZCIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAiLCJjdXN0b21lcklkIjoiMTM4MTQwMDAtMWRkMi0xMWIyLTgwODAtODA4MDgwODA4MDgwIiwiaXNzIjoidGhpbmdzYm9hcmQuaW8iLCJpYXQiOjE2NzIyMTk3NzIsImV4cCI6MTY3MjIyODc3Mn0.WM-9XIxoLvVyvX5vI4OJAXwg8I94vPozErmKn5ooea2gzpi58VqqjggfH3kHDVd2h0NH8j2QuZp15HzWa-WUmQ",
    }
    response = requests.get(
        "http://172.16.12.207:30909/api/tenant/info/55271cb0-76dd-11ed-8e2f-7bf1454332ad",
        headers=_req_header,
        timeout=10,
    )
    json_response = response.json()
    print(response.json())
    print("abc")


if __name__ == "__main__":
    main()
