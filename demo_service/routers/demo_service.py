from typing import Union, Optional
import fastapi
from fastapi import status, Depends, Cookie
import requests
import json
import stores.mykeycloak
from fastapi import HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    OAuth2AuthorizationCodeBearer,
)
from loguru import logger
import requests
from keycloak import KeycloakOpenID, KeycloakAdmin

router = fastapi.APIRouter()

# oauth2_scheme = OAuth2PasswordBearer()

kc_scheme = HTTPBearer()
BASE_URL = "http://127.0.0.1:8077"
_url = "http://127.0.0.1:8080"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "91djjv6bCPQhDa8WndrnyQdIsB0pF3Cd"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    client_secret_key=_client_secret,
)


def decode_token(token):

    KEYCLOAK_PUBLIC_KEY = (
        "-----BEGIN PUBLIC KEY-----\n"
        + keycloak_openid.public_key()
        + "\n-----END PUBLIC KEY-----"
    )
    logger.info(KEYCLOAK_PUBLIC_KEY)
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
    try:
        token_info = keycloak_openid.decode_token(
            token, key=KEYCLOAK_PUBLIC_KEY, options=options
        )

    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        ) from e
    logger.info(f"token info : {token_info}")
    return token_info


def manual_login(username, password):
    body = {
        "client_id": _client_id,
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_secret": _client_secret,
    }

    response = requests.post(
        f"{_url}/realms/{_realms}/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )

    return response.json()


@router.get("/")
async def hello_world():
    return "hello world"


@router.post("/manual_login", tags=["login"])
async def manual_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = manual_login(form_data.username, form_data.password)
    return token


@router.post("/lib_login", tags=["login"])
async def lib_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = keycloak_openid.token(form_data.username, form_data.password)
    return token


@router.get("/authorize", tags=["login"])
async def get_access_code():
    url = keycloak_openid.auth_url(BASE_URL + "/oauth/token2")
    logger.info(f"{url}")
    response = RedirectResponse(url)
    return response


@router.get("/oauth/token", tags=["login"])
async def get_access_code_redirect(response: Response, code):
    token = keycloak_openid.token(
        grant_type=["authorization_code"],
        code=code,
        redirect_uri=BASE_URL + "/oauth/token",
    )
    response.set_cookie(key="token", value=token)
    return "login successful, token stored in cookie"


@router.get("/oauth/token2", tags=["login"])
async def get_access_code_redirect(response: Response, code):
    token = keycloak_openid.token(
        grant_type=["authorization_code"],
        code=code,
        redirect_uri=BASE_URL + "/oauth/token",
    )
    response.set_cookie(key="token", value=token)
    return "login successful, token stored in cookie"


@router.get("/oauth/logout/1", tags=["logout"])
async def logout(response: Response, token: Union[str, None] = Cookie(dfault=None)):
    result = keycloak_openid.logout(
        json.loads(token.replace("'", '"'))["refresh_token"]
    )
    response.delete_cookie("token")
    return result
