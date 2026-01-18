import asyncio
from contextlib import asynccontextmanager
import datetime

import anyio
import orjson
import uvloop
from fastapi import FastAPI, Request, Response

import msgspec

from typing import List


class Cliente(msgspec.Struct):
    nome: str
    score: int
    vip: bool


class DadosPedido(msgspec.Struct):
    cliente: Cliente
    valorTotal: float
    descontoAplicado: float
    produtosComprados: List[str]


class ResponseRules(msgspec.Struct):
    resultado: dict
    createdAt: datetime.datetime = msgspec.field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


decoder = msgspec.json.Decoder(DadosPedido)
encoder = msgspec.json.Encoder()

uvloop.install()

regra_one = {
    "tipo": "json",
    "condicao": "dados.cliente.score > 700 and dados.valorTotal > 1000",
    "payload_retorno": {
        "codigo": "APROVADO",
        "descricao": "Desconto de 10 aplicado devido ao Score.",
        "tipo": "DESCONTO_10",
    },
}

regra_tow = {
    "tipo": "json",
    "condicao": "dados.cliente.vip == True and 'ALIMENTO' in dados.produtosComprados",
    "payload_retorno": {
        "codigo": "AVISO",
        "descricao": "Cliente VIP comprou ALIMENTO. Requer aprovação manual.",
        "tipo": "MANUAL_REVIEW",
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 600

    regra_one["condicao"] = compile(regra_one["condicao"], "<string>", "eval")
    regra_tow["condicao"] = compile(regra_tow["condicao"], "<string>", "eval")

    print("regras compiladas")

    yield


app = FastAPI(
    title="Dynamic Rule Evaluator API",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def evaluate_rule_boolean(json_pedido: DadosPedido, regra: dict) -> str:
    resultado_bool = eval(regra["condicao"], {}, {"dados": json_pedido})
    return str(resultado_bool).lower()


def evaluate_rule_json(json_pedido: DadosPedido, regra: dict) -> str:
    return (
        regra["payload_retorno"]
        if eval(regra["condicao"], {}, {"dados": json_pedido})
        else {"status": "REPROVADO", "payload": "Regra JSON falsa"}
    )


methods_dispatcher = {
    "boolean": evaluate_rule_boolean,
    "json": evaluate_rule_json,
}


@app.post("/regras", summary="Avalia uma regra dinamicamente.")
async def evaluate_rule(request: Request = None):
    body_bytes = await request.body()
    dados = decoder.decode(memoryview(body_bytes))

    evaluator_func = methods_dispatcher.get(regra_one["tipo"])
    resultado = evaluator_func(dados, regra_one)
    response_rules = ResponseRules(resultado=resultado)
    
    return Response(content=encoder.encode(response_rules), media_type="application/json")


@app.post("/body")
async def root_body(request: Request):
    raw = await request.body()
    body = orjson.loads(memoryview(raw))

    res = await controller_business_manager_rules_handler(body=body)

    return Response(orjson.dumps(res), media_type="application/json")


async def controller_business_manager_rules_handler(body):
    await asyncio.sleep(0.001)  # Simula operação assíncrona
    return body


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
