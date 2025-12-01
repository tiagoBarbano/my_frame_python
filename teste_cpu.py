from contextlib import asynccontextmanager
import anyio
from fastapi import FastAPI, Request
from granian import Granian
import orjson
from typing import Any
from fastapi.responses import ORJSONResponse

import uvloop

uvloop.install()

regra_one = {
    "tipo": "json",
    "condicao": "dados['cliente']['score'] > 700 and dados['valorTotal'] > 1000",
    "payload_retorno": {
        "codigo": "APROVADO",
        "descricao": "Desconto de 10 aplicado devido ao Score.",
        "tipo": "DESCONTO_10",
    },
}

regra_tow = {
    "tipo": "json",
    "condicao": "dados['cliente']['vip'] == True and 'ALIMENTO' in dados['produtosComprados']",
    "payload_retorno": {
        "codigo": "AVISO",
        "descricao": "Cliente VIP comprou ALIMENTO. Requer aprovação manual.",
        "tipo": "MANUAL_REVIEW",
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200

    regra_one['condicao'] = compile(regra_one['condicao'], "<string>", "eval")
    regra_tow['condicao'] = compile(regra_tow['condicao'], "<string>", "eval")

    print("regras compiladas")

    yield


app = FastAPI(
    title="Dynamic Rule Evaluator API",
    lifespan=lifespan,
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
)


def evaluate_rule_boolean(json_pedido: dict[str, Any], regra: dict) -> str:
    resultado_bool = eval(regra["condicao"], {}, {"dados": json_pedido})
    return str(resultado_bool).lower()


def evaluate_rule_json(json_pedido: dict[str, Any], regra: dict) -> str:
    resultado = eval(regra["condicao"], {}, {"dados": json_pedido})
    return regra["payload_retorno"] if resultado else {"status": "REPROVADO", "payload": "Regra JSON falsa"}


methods_dispatcher = {
    "boolean": evaluate_rule_boolean,
    "json": evaluate_rule_json,
}


@app.post("/evaluate", summary="Avalia uma regra dinamicamente.")
async def evaluate_rule(request: Request):
    body_bytes = await request.body()
    request_data = orjson.loads(memoryview(body_bytes))
    evaluator_func = methods_dispatcher.get(regra_one["tipo"])
    resultado = evaluator_func(request_data["json_pedido"], regra_one)
    return ORJSONResponse(content=resultado)


if __name__ == "__main__":
    workers = 2

    Granian(
        "teste_cpu:app",
        address="0.0.0.0",
        port=8000,
        interface="asgi",
        workers=workers,
        runtime_mode="st",
        backlog=16384,
        backpressure=4096,
        loop="uvloop",
        task_impl="asyncio",
        websockets=False,
        log_enabled=False,
    ).serve()
