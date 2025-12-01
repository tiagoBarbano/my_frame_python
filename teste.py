import time
import asyncio
import anyio
import sys
from concurrent.futures import ProcessPoolExecutor

try:
    import uvloop
except ImportError:
    uvloop = None


# 🔹 Exemplo de regra já compilada
rule_str = (
    "tipo_seguro in (0,6) and categoria_tarifaria in [20, 21, 22, 23] "
    "and classe_localizacao == 18 and lmi_casco >= 100000 "
    "and 2 <= score_serasa <= 900 and segmento_bancario not in [4, 6] "
    "and carrinhos <= 3 and nivel_relacionamento <= 3 "
    "and regiao_tarifaria in [305, 306, 308, 652, 653, 655, 659, 662, 667, 668, 661] "
    "and any(c in [1, 18, 19, 20] for c in cobertura) "
    "and taxa_ctt > 0.0025"
)
compiled_rule = compile(rule_str, "<string>", "eval")

# 🔹 Contexto de teste
context = {
    "tipo_seguro": 0,
    "categoria_tarifaria": 22,
    "classe_localizacao": 18,
    "lmi_casco": 200000,
    "score_serasa": 500,
    "segmento_bancario": 3,
    "carrinhos": 2,
    "nivel_relacionamento": 2,
    "regiao_tarifaria": 659,
    "cobertura": [1, 5, 10],
    "taxa_ctt": 0.003,
}

# ============================================================
# 🔹 Estratégias de avaliação
# ============================================================

def eval_direct():
    return eval(compiled_rule, {}, context)

async def eval_direct_async():
    return eval(compiled_rule, {}, context)

async def eval_threadpool():
    return await anyio.to_thread.run_sync(eval, compiled_rule, {}, context)

# precisa mandar string, não code object
def eval_in_process(rule_str, context):
    code = compile(rule_str, "<string>", "eval")
    return eval(code, {}, context)

process_executor = ProcessPoolExecutor()

async def eval_processpool():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_executor, eval_in_process, rule_str, context)

# ============================================================
# 🔹 Benchmarks
# ============================================================

async def benchmark(func, n=10_000, is_async=False):
    start = time.perf_counter()
    if is_async:
        for _ in range(n):
            await func()
    else:
        for _ in range(n):
            func()
    elapsed = time.perf_counter() - start
    print(f"{func.__name__:<20} -> {n} exec em {elapsed:.4f}s "
          f"({(n/elapsed):,.0f} ops/s)")


async def bench_event_loop(name, n=100_000):
    async def dummy_io():
        await asyncio.sleep(0)

    start = time.perf_counter()
    for _ in range(n):
        await dummy_io()
    elapsed = time.perf_counter() - start
    print(f"{name:<20} -> {n} ops em {elapsed:.4f}s "
          f"({(n/elapsed):,.0f} ops/s)")


# ============================================================
# 🔹 Execução
# ============================================================

async def main_eval():
    print(f"Python: {sys.version}")
    print("\n--- Bench Eval ---")
    await benchmark(eval_direct, n=100_000, is_async=False)
    await benchmark(eval_direct_async, n=100_000, is_async=True)    
    await benchmark(eval_threadpool, n=10_000, is_async=True)
    # await benchmark(eval_processpool, n=1_000, is_async=True)

    process_executor.shutdown()


def main_event_loops():
    print("\n--- Bench Event Loops ---")

    # asyncio padrão
    asyncio.run(bench_event_loop("asyncio stdlib"))

    # anyio rodando sobre asyncio
    async def anyio_runner():
        await bench_event_loop("anyio+asyncio")
    anyio.run(anyio_runner, backend="asyncio")

    # uvloop
    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(bench_event_loop("uvloop"))
    else:
        print("uvloop não instalado")


if __name__ == "__main__":
    asyncio.run(main_eval())
    main_event_loops()
