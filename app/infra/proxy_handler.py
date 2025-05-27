"""
File responsável por realizar integrações externas através do AioHTTP
"""

import asyncio
from contextlib import asynccontextmanager
import aiohttp
import ujson
import base64

from typing import Any
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.propagate import inject

from app.config import get_settings
from app.core.logger import log as logger


AioHttpClientInstrumentor().instrument()
settings = get_settings()


TIMEOUT = 2
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip",
}


class SessionManager:
    """Classe responsável por gerencia a Sessão do aioHttp"""

    _session: aiohttp.ClientSession | None = None

    @classmethod
    def init(cls):
        cls._session: aiohttp.ClientSession | None = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """Método responsável por obter a conexao do aiohttp"""
        if not cls._session:
            cls._session = aiohttp.ClientSession(json_serialize=ujson.dumps)
        return cls._session

    @classmethod
    async def close_session(cls):
        """Método responsável por fechar a conexao do aiohttp"""
        if cls._session:
            await cls._session.close()
            cls._session = None

            
    @classmethod
    @asynccontextmanager
    async def connection(cls):
        """Gerencia o contexto da sessão"""
        client = await cls.get_session()
        try:
            yield client
        finally:
            # Pode incluir lógica extra aqui se quiser
            pass

    async def processa_api(
        self, etapa_modulo: dict, request: dict, url_api: str, params: dict
    ):
        """
        Método responsável por realizar chamadas externas para APIs REST.
        Suporta:
        - POST com JSON no body.
        - GET com query params.
        - GET com path params (substituindo placeholders na URL).
        """

        try:
            inject(HEADERS)
            verbo_http: str = etapa_modulo.get("method").lower()
            auth_config: str = etapa_modulo.get("auth_config", None)
            headers_fields = etapa_modulo.get("header_fields", None)
            if headers_fields:
                HEADERS.update(headers_fields)

            if auth_config:
                token = await self.get_auth_token(auth_config)
                HEADERS.setdefault("Authorization", token)

            async with self.connection.request(
                method=verbo_http.upper(),
                url=url_api,
                json=request if verbo_http == "post" else None,
                params=params,
                headers=HEADERS,
                verify_ssl=False,
                timeout=TIMEOUT,
            ) as response:
                if response.status == 200:
                    resposta = {
                        "status": response.status,
                        "result": await response.json(),
                    }
                elif response.status == 204:
                    resposta = {
                        "status": response.status,
                        "result": "registro nao encontrado",
                    }
                else:
                    resposta = {
                        "status": response.status,
                        "result": await response.json(),
                    }

            return resposta

        except asyncio.TimeoutError as ex:
            logger.error("Timeout Error: %s - URL: %s", str(ex), url_api)
            return {"status": 504, "result": f"{str(ex)} - URL: {url_api}"}

        except Exception as ex:
            logger.error("Erro inesperado: %s", str(ex))
            return {"status": 500, "result": f"{str(ex)} - URL: {url_api}"}

    async def get_auth_token(auth_config: dict):
        """
        Obtém um token de autenticação baseado no método configurado.
        Pode ser Bearer Token (OAuth), API Key ou Basic Auth.
        """

        auth_type = auth_config.get("auth_type", "bearer")
        auth_url = auth_config.get("auth_url", "")
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }  # Garante que usamos os headers corretos

        if auth_type == "bearer":
            payload = auth_config.get("body", {})

            # Converte o JSON em formato x-www-form-urlencoded
            form_data = aiohttp.FormData()
            for key, value in payload.items():
                form_data.add_field(key, str(value))

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    auth_url, data=form_data, headers=headers, verify_ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"{data.get('token_type')} {data.get('access_token')}"
                    else:
                        raise Exception(f"Erro ao obter token: {response.status}")

        elif auth_type == "api_key":
            return auth_config.get("api_key")  # Apenas retorna a chave já cadastrada

        elif auth_type == "basic":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            basic_token = base64.b64encode(f"{username}:{password}".encode()).decode()
            return f"Basic {basic_token}"

        else:
            raise Exception("Método de autenticação não suportado")

    async def generate_dynamic_body(
        self, example_json: dict[str, Any], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Gera um body dinâmico baseado em um JSON de exemplo e nos dados de entrada.

        - Se o campo for um dicionário, ele processa recursivamente.
        - Se for uma lista de dicionários, faz o mesmo para cada item.
        - Se for um valor simples, apenas copia.
        """
        generated_body = {}

        for key, example_value in example_json.items():
            request_value = request_data.get(key)

            if isinstance(example_value, dict):  # Objeto aninhado
                generated_body[key] = self.generate_dynamic_body(
                    example_value, request_value or {}
                )
            elif (
                isinstance(example_value, list)
                and example_value
                and isinstance(example_value[0], dict)
            ):
                generated_body[key] = [
                    self.generate_dynamic_body(example_value[0], item)
                    for item in (request_value or [])
                ]
            else:  # Valor simples
                generated_body[key] = request_value

        return generated_body
