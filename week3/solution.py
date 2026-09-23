"""
Лабораторная работа 3. joblib.Parallel + Монте-Карло оценка Pi.

Реализация parallel_estimate_pi() поверх joblib.Parallel/delayed и
benchmark-харнесс, замеряющий время при n_jobs = 1, 2, 4, -1 (все ядра).

Запуск:
    # быстрая проверка последовательного и параллельного результата
    python solution.py --variant 5

    # полный замер + сохранение JSON
    python solution.py --variant 5 --benchmark --repeats 3 --out results/bench.json
"""
import argparse
import json
import os
import statistics
import time
from pathlib import Path

from joblib import Parallel, delayed

from starter import (
    estimate_pi_batch,
    sequential_estimate_pi,
    variant_params,
)


def parallel_estimate_pi(n_batches, points_per_batch, seed, n_jobs):
    """joblib-версия sequential_estimate_pi.

    Каждый батч — независимый вызов estimate_pi_batch(points_per_batch, seed + b),
    joblib.Parallel собирает результаты в список, затем суммируем и делим на
    общее число точек, как в оригинале.
    """
    inside_per_batch = Parallel(n_jobs=n_jobs)(
        delayed(estimate_pi_batch)(points_per_batch, seed + b)
        for b in range(n_batches)
    )
    total_inside = sum(inside_per_batch)
    total_points = n_batches * points_per_batch
    return 4.0 * total_inside / total_points


def measure(fn, repeats: int):
    samples = [fn() for _ in range(repeats)]
    return {
        "min": min(samples),
        "median": statistics.median(samples),
        "samples": samples,
    }


def benchmark(variant: int, repeats: int, out_path: Path | None):
    n_batches, points_per_batch, seed = variant_params(variant)
    cpu = os.cpu_count()
    print(f"Вариант {variant}: n_batches={n_batches}, points_per_batch={points_per_batch}, "
          f"seed={seed}, logical CPUs={cpu}")

    # baseline — оригинальный sequential_estimate_pi (без joblib)
    def run_seq():
        t0 = time.perf_counter()
        pi = sequential_estimate_pi(n_batches, points_per_batch, seed)
        return time.perf_counter() - t0, pi

    def run_par(n_jobs):
        def _one():
            t0 = time.perf_counter()
            pi = parallel_estimate_pi(n_batches, points_per_batch, seed, n_jobs)
            return time.perf_counter() - t0, pi
        return _one

    def measure_pi(one_call, repeats):
        times, pis = [], []
        for _ in range(repeats):
            dt, pi = one_call()
            times.append(dt)
            pis.append(pi)
        return {
            "min": min(times),
            "median": statistics.median(times),
            "samples": times,
            "pi_last": pis[-1],
        }

    results = {
        "variant": variant,
        "n_batches": n_batches,
        "points_per_batch": points_per_batch,
        "seed": seed,
        "cpu_count": cpu,
        "repeats": repeats,
        "data": {},
    }

    r = measure_pi(run_seq, repeats)
    results["data"]["sequential"] = r
    print(f"  sequential            min={r['min']:.3f} с  median={r['median']:.3f} с  Pi≈{r['pi_last']:.5f}")

    for n_jobs in (1, 2, 4, -1):
        r = measure_pi(run_par(n_jobs), repeats)
        results["data"][f"n_jobs={n_jobs}"] = r
        print(f"  joblib n_jobs={n_jobs:>2}     min={r['min']:.3f} с  median={r['median']:.3f} с  Pi≈{r['pi_last']:.5f}")

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\nСохранено: {out_path}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    parser.add_argument("--benchmark", action="store_true",
                        help="Прогнать полный замер n_jobs=1,2,4,-1")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.benchmark:
        benchmark(args.variant, args.repeats, args.out)
        return

    n_batches, points_per_batch, seed = variant_params(args.variant)
    print(f"Вариант {args.variant}: n_batches={n_batches}, points_per_batch={points_per_batch}, seed={seed}")

    t0 = time.perf_counter()
    pi_seq = sequential_estimate_pi(n_batches, points_per_batch, seed)
    t1 = time.perf_counter()
    print(f"sequential  Pi≈{pi_seq:.5f}  за {t1 - t0:.3f} с")

    t0 = time.perf_counter()
    pi_par = parallel_estimate_pi(n_batches, points_per_batch, seed, n_jobs=-1)
    t1 = time.perf_counter()
    print(f"joblib -1   Pi≈{pi_par:.5f}  за {t1 - t0:.3f} с")

    assert abs(pi_seq - pi_par) < 1e-12, "sequential и joblib дают разные суммы!"


if __name__ == "__main__":
    main()
