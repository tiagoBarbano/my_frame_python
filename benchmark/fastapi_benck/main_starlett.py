import asyncio
import aiohttp
import orjson
from redis.asyncio import Redis

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response, JSONResponse
from starlette.requests import Request
from contextlib import asynccontextmanager

session: aiohttp.ClientSession | None = None
redis: Redis | None = None


@asynccontextmanager
async def lifespan(app):
    global session, redis
    session = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300),
        timeout=aiohttp.ClientTimeout(total=3),
    )
    redis = Redis(
        host="localhost",
        port=6379,
        password="redis1234",
        decode_responses=True,
        db=1,
    )
    yield
    await session.close()
    await redis.close()


async def homepage(request: Request):
    return JSONResponse({"hello": "world"})


async def get_cep(request: Request):
    cep = request.path_params["cep"]
    if not cep.isdigit() or len(cep) != 8:
        return Response(
            content='{"detail": "CEP inválido"}'.encode("utf-8"),
            status_code=422,
            media_type="application/json",
        )

    cache_key = f"cep:{cep}"
    cached = await redis.get(cache_key)
    if cached:
        return Response(
            content=cached.encode(),
            media_type="application/json"
        )

    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return Response(
                    content=b'{"detail": "Erro ao acessar ViaCEP"}',
                    status_code=502,
                    media_type="application/json",
                )
            data = await resp.json()

            if "erro" in data:
                return Response(
                    content='{"detail": "CEP não encontrado"}'.encode("utf-8"),
                    status_code=404,
                    media_type="application/json",
                )

            payload = orjson.dumps(data)
            await redis.set(cache_key, payload.decode(), ex=600)

            return Response(
                content=payload,
                media_type="application/json"
            )

    except asyncio.TimeoutError:
        return Response(
            content='{"detail": "Timeout na requisição ao ViaCEP"}'.encode("utf-8"),
            status_code=504,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=orjson.dumps({"detail": f"Erro inesperado: {str(e)}"}),
            status_code=500,
            media_type="application/json"
        )


app = Starlette(
    debug=False,
    routes=[
        Route("/", homepage),
        Route("/cep/{cep}", get_cep),
    ],
    lifespan=lifespan,
)
