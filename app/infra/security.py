# import requests
# from fastapi.security import OAuth2PasswordBearer

# from authlib.jose import JsonWebToken
# from fastapi import Depends, HTTPException, Security, status

# from api.config import get_settings
# from api.core.observability import logger
# from urllib3.exceptions import InsecureRequestWarning
# from urllib3 import disable_warnings

# settings = get_settings()
# disable_warnings(InsecureRequestWarning)

# jwks = requests.get(
#     url=settings.jks_url,
#     verify=settings.requests_ca_bundle,
#     proxies={"https": "", "http": ""},
# ).json()

# jwt = JsonWebToken(algorithms="RS256")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.token_url)


# async def validar_token(authorization: str = Depends(oauth2_scheme)) -> bool:
#     """
#     Responsável por validar o token oAuth utilziadno o JWKS

#     Args:
#         authorization (str, optional): _description_. Defaults to Depends(oauth2_scheme).

#     Raises:
#         HTTPException: Informa problema na validação do token

#     Returns:
#         _type_: bool
#     """
#     try:
#         jwt.decode(authorization, jwks).validate()
#         return True
#     except Exception as ex:
#         logger.error("Erro ao verificar o token", extra={"Error": str(ex)})
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail={"error": "Erro ao verificar o token"},
#         )


# async def verifica_token(flag: bool = Security(validar_token)) -> bool:
#     return flag
