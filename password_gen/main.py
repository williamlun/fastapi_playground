import secrets
import string
import fastapi
from fastapi import Body
import uvicorn


char_pool = string.ascii_letters + string.digits
pwd_length = 16
app = fastapi.FastAPI()


def password(length=pwd_length, chars=char_pool):
    return "".join(secrets.choice(chars) for _ in range(length))


def add_password(text):
    records = text.split("\n")
    result = []
    for record in records:
        newpassword = password()
        result.append(record.replace('""', newpassword))
    return result


@app.post("/generate")
def generate_password(text: str = Body(...)):
    result = add_password(text)
    print(result)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
