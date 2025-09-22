from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import asyncio

app = FastAPI()

# Função pesada (roda em uma thread separada)
def heavy_workload(n: int) -> str:
    return "Hello,World!"

@app.get("/")
async def root():
    # roda a função em uma thread separada
    result = await asyncio.to_thread(heavy_workload, 42)
    return ORJSONResponse(content={"msg": result})
