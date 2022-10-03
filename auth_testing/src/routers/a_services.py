from lib2to3.pgen2 import token
import fastapi
from fastapi import status, Depends
import exceptions
import services.auth
import requests
import stores.mykeycloak
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    OAuth2AuthorizationCodeBearer,
)
from loguru import logger

router = fastapi.APIRouter()

# oauth2_scheme = OAuth2PasswordBearer()
kc_scheme = HTTPBearer()


@router.get("/")
async def hello_world():
    return "hello world"


@router.get("/redirect/1")
async def redirect():
    body = {
        "response_type": "code",
        "client_id": "fastapi_play",
    }
    # response = requests.post(
    #     "http://127.0.0.1:30769/realms/atal/protocol/openid-connect/auth",
    #     headers={"Content-Type": "application/x-www-form-urlencoded"},
    #     data=body,
    # )
    print("HI")
    return "HI"


@router.get("/redirect/2")
async def redirect2(session_state, code):
    print(session_state)
    print(code)
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8077/a/v1/redirect/2",
        "client_id": "fastapi_play",
        "client_secret": "Xmyejkc5ngfLo8t23WnXOl7bB6bgUqJa",
    }
    response = requests.post(
        "http://127.0.0.1:30769/realms/atal/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    return response.json()


@router.get("/redirect/3")
async def redirect3():
    client_id = "fastapi_play"
    redirect_uri = "http://127.0.0.1:8077/a/v1/redirect/2"
    response_type = "code"
    response = RedirectResponse(
        f"http://127.0.0.1:30769/realms/atal/protocol/openid-connect/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}"
    )

    return response


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = services.auth.login(form_data.username, form_data.password)
    return token


async def decode_token(token: HTTPAuthorizationCredentials = Depends(kc_scheme)):
    logger.info(f"HTTPAuthorizationCredentials: {token}")
    return stores.mykeycloak.decode_token(token.credentials)


async def obtain_user_profile(token: dict = Depends(decode_token)) -> dict:
    keycloak_user_id = token["sub"]
    fake_db = {"01297653-fccb-48bd-8dec-d6a8f8fba255": {"scopes": ["all-rights"]}}

    try:
        return fake_db[keycloak_user_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        )


@router.get("/demo-get-with-auth")
def demo_get_with_auth(user_profile: dict = Depends(obtain_user_profile)):

    if "get:me" not in user_profile["scopes"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user_profile


@router.get("/demo-get-with-simple-auth")
def demo_get_with_auth(token: dict = Depends(decode_token)):
    return token


@router.get("/logout/1")
def logout1():
    redirect_uri = "http://127.0.0.1:8077/docs#"
    client_id = "fastapi_play"
    response = RedirectResponse(
        f"http://127.0.0.1:30769/realms/atal/protocol/openid-connect/logout?client_id={client_id}"
    )
    return response


# ?client_id={client_id}&redirect_uri={redirect_uri}


@router.get("/logout/2")
def logout1(token: HTTPAuthorizationCredentials = Depends(kc_scheme)):
    redirect_uri = "http://127.0.0.1:8077/docs#"
    response = requests.post(
        f"http://127.0.0.1:30769/realms/atal/protocol/openid-connect/logout?redirect_uri={redirect_uri}",
    )


# Config login Redirect URI or Callback URL -> Implement OAuth Flow in (alarm) service
# decode access token in fastapi

# config service account for internal services -> Implement service internal commmunication

# import client, service account info to keycloak -> Import client configuration to Keycloak
