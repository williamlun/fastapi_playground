from multiprocessing.managers import Token
from typing import Union, Optional
import fastapi
from fastapi import status, Depends, Cookie
import requests
import json
import stores.mykeycloak
from fastapi import HTTPException, status, Response, Request
import keycloak.exceptions
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
_url = "http://127.0.0.1:9090"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "11DZhQr51uTUf2jSPO0aIV4Z9Tt5J6NZ"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    client_secret_key=_client_secret,
)


KEYCLOAK_PUBLIC_KEY = (
    "-----BEGIN PUBLIC KEY-----\n"
    + keycloak_openid.public_key()
    + "\n-----END PUBLIC KEY-----"
)


def decode_token(token):
    logger.info(KEYCLOAK_PUBLIC_KEY)
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
    try:
        token_info = keycloak_openid.decode_token(
            token, key=KEYCLOAK_PUBLIC_KEY, options=options
        )

    except (HTTPException, BaseException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        ) from e
    logger.info(f"token info : {token_info}")
    return token


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


def get_token(token: Optional[str] = Cookie(None)):
    if not token:
        logger.info("token not provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="HTTP_403_FORBIDDEN"
        )
    token_json = json.loads(token.replace("'", '"'))
    return decode_token(token_json["access_token"])


@router.get("/")
async def hello_world():
    return "hello world"


@router.get("/redirect")
async def redirect_uri(
    response: Response,
    state: str,
    code: Union[str, None] = None,
):
    logger.info(f"code: {code}")
    return code


@router.get("/a")
async def hello_world_with_auth(token=Depends(get_token)):
    return "hello world with auth"


# @router.post("/manual_login", tags=["login"])
# async def manual_login(form_data: OAuth2PasswordRequestForm = Depends()):
#     token = manual_login(form_data.username, form_data.password)
#     return token


@router.post("/login", tags=["login"])
async def lib_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = keycloak_openid.token(form_data.username, form_data.password)
    return token


# @router.get("/authorize2", tags=["login"])
# async def get_access_code_2():
#     url = keycloak_openid.auth_url(BASE_URL + "/oauth/token")
#     logger.info(f"{url}")
#     response = RedirectResponse(url)
#     return response


@router.get("/authorize", tags=["login"])
async def get_access_code(
    state: str = "123",
    redir_url: str = "http://127.0.0.1:8077/redirect",
):
    url = keycloak_openid.auth_url(redir_url, state=state)
    logger.info(f"{url}")
    response = RedirectResponse(url)
    return response


@router.get("/oauth/token", tags=["login"])
async def get_access_code_redirect(
    response: Response,
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = "http://127.0.0.1:8077/redirect",
    code: str = None,
):
    if code:
        token = keycloak_openid.token(
            grant_type=["authorization_code"], code=code, redirect_uri=redirect_uri
        )
    else:
        token = keycloak_openid.token(
            grant_type=["client_credentials"],
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
    response.set_cookie(key="token", value=token)
    return {"message": "login successful, token stored in cookie", "token": token}


@router.get("/oauth/logout", tags=["logout"])
async def logout(response: Response, token: Optional[str] = Cookie(None)):
    if not token:
        return "token not found."
    result = keycloak_openid.logout(
        json.loads(token.replace("'", '"'))["refresh_token"]
    )
    logger.info(f" logout output: {result}")
    response.delete_cookie("token")
    return "logout successfully"


@router.get("/site_a/device_a/")
@router.get("/get_user_permissions", tags=["auth"])
async def get_user_permissions(token=Depends(get_token)):
    # keycloak_openid.load_authorization_config(
    #     "/Users/williamleung/Documents/fastapi_playground/demo_service/test-authz-config.json"
    # )
    permissions = keycloak_openid.uma_permissions(token)
    logger.info(f"permissions : {permissions}")
    return "hi"


@router.get("/get_user_permissions_specific", tags=["auth"])
async def get_user_permissions(token=Depends(get_token)):
    # keycloak_openid.load_authorization_config(
    #     "/Users/williamleung/Documents/fastapi_playground/demo_service/test-authz-config.json"
    # )
    try:
        permissions = keycloak_openid.uma_permissions(
            token, permissions="resouce_a#view"
        )
        logger.info(f"permissions : {permissions}")
    except keycloak.exceptions.KeycloakError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        )
    return "hi"


@router.get("/get_user_permissions_auth_status", tags=["auth"])
async def get_user_permissions_auth_status(token=Depends(get_token)):
    auth_status = keycloak_openid.has_uma_access(token, "resourcasdfg#read")
    logger.info(f"auth_status: {auth_status}")
    return auth_status
