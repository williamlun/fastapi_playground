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
_url = "http://127.0.0.1:8080"
_realms = "atal"
_client_id = "demo_service"
_client_secret = "Oav1GLwKZdDIBySvnMv7tGgZJjwZyqGh"

keycloak_openid = KeycloakOpenID(
    server_url=_url,
    client_id=_client_id,
    realm_name=_realms,
    client_secret_key=_client_secret,
)

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="user_super_admin",
    password="p",
    realm_name="atal",
    verify=True,
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


@router.post("/manual_login", tags=["login"])
async def manual_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = manual_login(form_data.username, form_data.password)
    return token


@router.post("/lib_login", tags=["login"])
async def lib_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = keycloak_openid.token(form_data.username, form_data.password)
    return token


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
async def get_user_permissions(token=Depends(get_token)):
    # keycloak_openid.load_authorization_config(
    #     "/Users/williamleung/Documents/fastapi_playground/demo_service/test-authz-config.json"
    # )
    permissions = keycloak_openid.uma_permissions(token)
    logger.info(f"permissions : {permissions}")
    return "hi"


@router.get("/demo_service/{site}/test", tags=["auth"])
async def get_test(code: str, site: str, token=Depends(get_token)):
    if code:
        logger.info(f"code = {code}")
    return "pass the token auth"


@router.get("/demo_service/{site}/devices/{device}", tags=["auth"])
async def get_user_permissions(site: str, token=Depends(get_token)):
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
async def get_user_permissions_auth_status(token=Depends(get_token)):
    auth_status = keycloak_openid.has_uma_access(token, "resourcasdfg#read")
    logger.info(f"auth_status: {auth_status}")
    return auth_status


###########################################################################
#########################TESTING##########################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
############################################################################
###########################################################################
###########################################################################


@router.get("/admin/user/list", tags=["admin"])
async def get_users():
    keycloak_admin.realm_name = "atal"
    users = keycloak_admin.get_users({})
    logger.info(f"user_list : {users}")
    user_id = "cf45447c-418c-4336-9c2a-88aa26f7c888"

    clients_id = keycloak_admin.get_client_id("demo")
    logger.info(f"clients: {clients_id}")

    consents = keycloak_admin.user_consents(user_id=user_id)
    logger.info(f"consents: %s" % consents)

    credentials = keycloak_admin.get_credentials(user_id=user_id)
    logger.info(f"credentials: %s" % credentials)

    realm_roles = keycloak_admin.get_realm_roles()
    logger.info(f"realm_roles: %s" % realm_roles)

    # Get all client authorization resources
    client_resources = keycloak_admin.get_client_authz_resources(client_id=clients_id)
    logger.info("Client authorization resources: %s" % client_resources)
    # Get all client authorization scopes
    client_scopes = keycloak_admin.get_client_authz_scopes(client_id=clients_id)
    logger.info("client_scopes: %s" % client_scopes)
    # Get all client authorization permissions
    client_permissions = keycloak_admin.get_client_authz_permissions(
        client_id=clients_id
    )
    logger.info("Client_permissions: %s" % client_permissions)
    # Get all client authorization policies
    client_policies = keycloak_admin.get_client_authz_policies(client_id=clients_id)
    logger.info("Client policies: %s" % client_policies)

    # Get all groups
    groups = keycloak_admin.get_groups()
    logger.info("Groups: %s" % groups)

    roles = keycloak_admin.get_client_roles(client_id=clients_id)
    logger.info("roles: %s" % roles)

    token = str(keycloak_admin._token)
    logger.info("token : %s" % token)
    access_token = json.loads(token.replace("'", '"'))["access_token"]
    logger.info("access_token : %s" % access_token)


@router.get("/admin/user/resource/test", tags=["admin"])
async def resource_test():
    keycloak_admin.realm_name = "atal"
    user_id = "ad6ceeb5-891a-4073-b328-1506406df42c"
    clients_id = keycloak_admin.get_client_id(_client_id)
    logger.info(f"clients: {clients_id}")
    payload = {
        "name": "test",
        "type": "site_test",
        "scopes": [
            {
                "id": "fbb2c8f6-4f10-4f75-84de-4b7812a0ce06",
                "name": "read",
                "iconUri": "",
            },
            {
                "id": "4193149b-ce2a-4daf-8401-010144ddb07f",
                "name": "write",
                "iconUri": "",
            },
        ],
        "uris": ["site/test/*"],
    }

    keycloak_admin.create_client_authz_resource(client_id=clients_id, payload=payload)


@router.get("/admin/user/scopes/test")
async def scopes_test():

    token = manual_login("user_admin", "p")

    refresh_token = json.loads(str(keycloak_admin._token).replace("'", '"'))[
        "refresh_token"
    ]
    logger.info("refresh_token token: %s" % refresh_token)

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "security-admin-console",
    }

    rep = requests.post(
        url="http://127.0.0.1:8080/realms/master/protocol/openid-connect/token",
        headers={"Content-Type": "application/json"},
        data=body,
    )
    logger.info(f"rep : {rep}")

    new_token = keycloak_admin.get_token()
    logger.info("New token: %s" % new_token)

    access_token = json.loads(str(keycloak_admin._token).replace("'", '"'))[
        "access_token"
    ]
    clients_id = keycloak_admin.get_client_id(_client_id)
    logger.info("Client id: %s" % clients_id)
    payload = {"name": "test_scpoes", "displayName": "", "iconUri": ""}
    url = (
        _url
        + f"/admin/realms/{_realms}/clients/{clients_id}/authz/resource-server/scope"
    )
    logger.info(f"url: {url}")
    response = requests.post(
        url=url,
        headers={
            f"Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    logger.info(f"{response}")
