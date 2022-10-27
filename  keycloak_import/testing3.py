import pydantic


class Tesing(pydantic.BaseModel):
    name: str
    number: int
    bu: bool


asdfa = Tesing(name=123, number="123", bu=True)

print(asdfa)
