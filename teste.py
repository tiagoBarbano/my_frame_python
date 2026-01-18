import inspect
import time
import asyncio
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import anyio


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

limiter = anyio.CapacityLimiter(8) 

async def eval_threadpool():
    return await anyio.to_thread.run_sync(eval, compiled_rule, {}, context, limiter=limiter)


# precisa mandar string, não code object
def eval_in_process(rule_str, context):
    code = compile(rule_str, "<string>", "eval")
    return eval(code, {}, context)


thread_executor = ThreadPoolExecutor(max_workers=22)
process_executor = ProcessPoolExecutor(max_workers=4)


async def eval_processpool():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        thread_executor, eval, rule_str, context
    )


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
    print(
        f"{func.__name__:<20} -> {n} exec em {elapsed:.4f}s "
        f"({(n / elapsed):,.0f} ops/s)"
    )
    
async def benchmark_parallel(func, n=50_000):
    start = time.perf_counter()

    async def runner():
        result = func()
        if inspect.isawaitable(result):
            await result

    async with anyio.create_task_group() as tg:
        for _ in range(n):
            tg.start_soon(runner)

    elapsed = time.perf_counter() - start
    print(
        f"{func.__name__:<25} -> {n} exec em {elapsed:.4f}s "
        f"({(n / elapsed):,.0f} ops/s)"
    )
    
# ============================================================
# 🔹 Execução
# ============================================================


async def main_eval():
    print(f"Python: {sys.version}")
    print("\n--- Bench Eval ---")
    await benchmark(eval_direct, n=10_000_000)
    await benchmark(eval_direct_async, n=10_000_000, is_async=True)
    await benchmark_parallel(eval_threadpool, n=10_000)
    await benchmark_parallel(eval_processpool, n=10_000)

    process_executor.shutdown()


if __name__ == "__main__":
    asyncio.run(main_eval())
