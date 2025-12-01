from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import asyncio
import random

app = FastAPI()

# Função pesada (roda em uma thread separada)
def heavy_workload(n: int) -> str:
    multi = n * 2
    return multi

@app.get("/")
async def root():
    # roda a função em uma thread separada
    result = await asyncio.to_thread(heavy_workload, random.random())
    return ORJSONResponse(content={"msg": result})

@app.get("/def")
async def root_def():
    # roda a função em uma thread separada
    result = heavy_workload(random.random())
    return ORJSONResponse(content={"msg": result})
