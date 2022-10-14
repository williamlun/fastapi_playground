from multiprocessing.managers import Token
from typing import Union, Optional
import fastapi
from fastapi import status, Depends, Cookie
import requests
import json
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
_url = "http://127.0.0.1:8080"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "hsRRjJta9TDb7s6gM6ChBOyTPt0sp8QM"

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


def get_cookie_token(token: Optional[str] = Cookie(None)):
    if not token:
        logger.info("token not provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        )
    token_json = json.loads(token.replace("'", '"'))
    return decode_token(token_json["access_token"])


def get_bearer_token(
    token: Optional[HTTPAuthorizationCredentials] = Depends(kc_scheme),
):
    logger.info(token)
    if not token:
        logger.info("token not provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        )

    return decode_token(token.credentials)


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
async def hello_world_with_auth(token=Depends(get_cookie_token)):
    return "hello world with auth"


@router.get("/authorize", tags=["login"])
async def get_access_code(
    client_id: str,
    state: str,
    redirect_uri: str,
):
    if client_id != _client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid client id."
        )
    url = keycloak_openid.auth_url(redirect_uri, state=state)
    logger.info(f"{url}")
    response = RedirectResponse(url)
    return response


@router.post("/token", tags=["login"])
async def get_access_code_redirect(
    response: Response,
    grant_type: str = None,
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None,
    code: str = None,
    refresh_token: str = None,
):
    if client_id != _client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid client id."
        )

    if grant_type == "authorization_code":
        token = keycloak_openid.token(
            grant_type=[grant_type], code=code, redirect_uri=redirect_uri
        )
    elif grant_type == "client_credentials":
        token = keycloak_openid.token(
            grant_type=[grant_type],
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
    elif grant_type == "refresh_token":
        token = keycloak_openid.refresh_token(refresh_token)

    response.set_cookie(key="token", value=token)
    return token


@router.get("/logout", tags=["logout"])
async def logout(response: Response, token: Optional[str] = Cookie(None)):
    if not token:
        return "token not found."
    result = keycloak_openid.logout(
        json.loads(token.replace("'", '"'))["refresh_token"]
    )
    logger.info(f" logout output: {result}")
    response.delete_cookie("token")
    return "logout successfully"


@router.get("/user/permissions", tags=["auth"])
async def get_user_permissions(token=Depends(get_cookie_token)):
    permissions = keycloak_openid.uma_permissions(token)
    logger.info(f"permissions : {permissions}")
    return {"permissions": permissions}


@router.get("/demo_service/data/a", tags=["demo"])
async def get_test_without_auth():
    data = "Data response without Authentication."
    return {"data": data}


@router.get("/demo_service/data/b", tags=["demo"])
async def get_test2(token=Depends(get_bearer_token)):
    data = "Data response with Authentication. (Get token from bearer)"
    return {"data": data}


@router.get("/demo_service/data/c", tags=["demo"])
async def get_test(token=Depends(get_cookie_token)):
    data = "Data response with Authentication. (Get token from cookie.)"
    return {"data": data}


@router.get("/demo_service/site/{site}/cookie", tags=["auth"])
async def get_test(code: str, site: str, token=Depends(get_cookie_token)):
    data = "Data response"
    return data


@router.get("/demo_service/site/{site}/devices/{device}", tags=["auth"])
async def get_user_permissions(site: str, token=Depends(get_cookie_token)):
    # keycloak_openid.load_authorization_config(
    #     "/Users/williamleung/Documents/fastapi_playground/demo_service/test-authz-config.json"
    # )
    try:
        permissions = keycloak_openid.uma_permissions(token, permissions=f"{site}#read")
        logger.info(f"permissions : {permissions}")
    except keycloak.exceptions.KeycloakError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="HTTP_401_UNAUTHORIZED"
        )
    return "pass"


@router.get("/user/auth/status", tags=["auth"])
async def get_user_permissions_auth_status(token=Depends(get_cookie_token)):
    auth_status = keycloak_openid.has_uma_access(token, "site_a_room101#read")
    logger.info(f"auth_status: {auth_status}")
    return auth_status
