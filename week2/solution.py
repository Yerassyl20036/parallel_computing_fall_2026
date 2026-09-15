"""
Лабораторная работа 2. threading vs multiprocessing.

Реализованы run_with_threads() и run_with_processes() — минимальные
реализации через threading.Thread и multiprocessing.Process (по n_workers
воркеров, каждый обрабатывает свою долю из n_tasks вызовов).

Запуск:
    # только реализация + одна пара цифр (быстрый sanity-check)
    python solution.py --variant 5

    # полный замер 2×3×2 (CPU/IO × 1/2/4 × threads/processes) + JSON
    python solution.py --variant 5 --benchmark --repeats 3 --out results/bench.json
"""
import argparse
import json
import multiprocessing
import os
import statistics
import threading
import time
from pathlib import Path

from starter import (
    cpu_bound_task,
    io_bound_task,
    run_sequential,
    variant_params,
)


def _split_tasks(n_tasks: int, n_workers: int):
    """Возвращает список из n_workers чисел — сколько задач достаётся каждому воркеру."""
    base, extra = divmod(n_tasks, n_workers)
    return [base + (1 if i < extra else 0) for i in range(n_workers)]


def _worker_loop(task_fn, arg, times):
    for _ in range(times):
        task_fn(arg)


def run_with_threads(task_fn, arg, n_tasks, n_workers):
    """Запускает n_tasks вызовов task_fn(arg) на n_workers threading.Thread-воркерах.
    Возвращает время выполнения (сек)."""
    shares = _split_tasks(n_tasks, n_workers)
    threads = [
        threading.Thread(target=_worker_loop, args=(task_fn, arg, share))
        for share in shares
    ]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - t0


def run_with_processes(task_fn, arg, n_tasks, n_workers):
    """Аналог run_with_threads на multiprocessing.Process."""
    shares = _split_tasks(n_tasks, n_workers)
    procs = [
        multiprocessing.Process(target=_worker_loop, args=(task_fn, arg, share))
        for share in shares
    ]
    t0 = time.perf_counter()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return time.perf_counter() - t0


def measure(fn, repeats=3):
    samples = [fn() for _ in range(repeats)]
    return {
        "min": min(samples),
        "median": statistics.median(samples),
        "samples": samples,
    }


def benchmark(variant: int, repeats: int, out_path: Path | None):
    n_tasks, cpu_n, io_sleep = variant_params(variant)
    print(f"Вариант {variant}: n_tasks={n_tasks}, cpu_n={cpu_n}, io_sleep={io_sleep:.2f} с, "
          f"logical CPUs={os.cpu_count()}")

    workloads = [
        ("cpu_bound",  cpu_bound_task, cpu_n),
        ("io_bound",   io_bound_task,  io_sleep),
    ]
    results = {
        "variant": variant,
        "n_tasks": n_tasks,
        "cpu_n": cpu_n,
        "io_sleep": io_sleep,
        "cpu_count": os.cpu_count(),
        "repeats": repeats,
        "data": {},
    }

    for wname, wfn, warg in workloads:
        print(f"\n=== {wname} ===")
        wblock = {}

        # sequential (baseline)
        r = measure(lambda: run_sequential(wfn, warg, n_tasks), repeats=repeats)
        wblock["sequential"] = r
        print(f"  sequential           min={r['min']:.3f} с  median={r['median']:.3f} с")

        for mode, runner in [("threads", run_with_threads), ("processes", run_with_processes)]:
            for w in (1, 2, 4):
                r = measure(lambda w=w, runner=runner: runner(wfn, warg, n_tasks, w),
                            repeats=repeats)
                wblock.setdefault(mode, {})[str(w)] = r
                print(f"  {mode:9} w={w}         min={r['min']:.3f} с  median={r['median']:.3f} с")

        results["data"][wname] = wblock

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\nСохранено: {out_path}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    parser.add_argument("--benchmark", action="store_true",
                        help="Прогнать полный 2×3×2 замер")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.benchmark:
        benchmark(args.variant, args.repeats, args.out)
        return

    # Быстрый sanity-check
    n_tasks, cpu_n, io_sleep = variant_params(args.variant)
    print(f"Вариант {args.variant}: n_tasks={n_tasks}, cpu_n={cpu_n}, io_sleep={io_sleep:.2f} с")

    t_seq_cpu = run_sequential(cpu_bound_task, cpu_n, n_tasks)
    t_seq_io  = run_sequential(io_bound_task,  io_sleep, n_tasks)
    t_thr_cpu = run_with_threads(cpu_bound_task, cpu_n, n_tasks, 4)
    t_prc_cpu = run_with_processes(cpu_bound_task, cpu_n, n_tasks, 4)
    print(f"CPU seq={t_seq_cpu:.3f}  threads(4)={t_thr_cpu:.3f}  processes(4)={t_prc_cpu:.3f}")
    print(f"I/O seq={t_seq_io:.3f}")


if __name__ == "__main__":
    main()
