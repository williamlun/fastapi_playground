from lib2to3.pgen2 import token
import fastapi
from fastapi import status, Depends
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


@router.post("/manual_login")
async def manual_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = stores.mykeycloak.manual_login(form_data.username, form_data.password)
    logger.info
    return token


@router.post("/lib_login")
async def lib_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = stores.mykeycloak.lib_login(form_data.username, form_data.password)
    return token
