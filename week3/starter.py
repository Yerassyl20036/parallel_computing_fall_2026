"""
Лабораторная работа 3. Параллелизация с joblib: Монте-Карло оценка числа Pi.

Дана последовательная реализация оценки числа Pi методом Монте-Карло
(случайные точки в квадрате [-1,1]x[-1,1], доля попавших в единичный круг).
Задача разбита на n_batches независимых партий (batch) — идеальный
embarrassingly parallel случай.

Ваша задача:
  1) реализовать parallel_estimate_pi() с помощью joblib.Parallel + delayed,
     распараллелив цикл по батчам;
  2) замерить время при n_jobs = 1, 2, 4, -1 (все ядра) и построить график
     ускорения (speedup) относительно n_jobs=1.

Запуск:
    python starter.py --variant <номер_варианта>
"""
import argparse
import random
import time


def variant_params(variant: int):
    variant = ((variant - 1) % 15) + 1
    n_batches = 8 + variant           # 9..23 батчей
    points_per_batch = 500_000 + (variant - 1) * 100_000
    seed = 2000 + variant * 13
    return n_batches, points_per_batch, seed


def estimate_pi_batch(n_points, seed):
    rng = random.Random(seed)
    inside = 0
    for _ in range(n_points):
        x = rng.uniform(-1, 1)
        y = rng.uniform(-1, 1)
        if x * x + y * y <= 1.0:
            inside += 1
    return inside


def sequential_estimate_pi(n_batches, points_per_batch, seed):
    total_inside = 0
    for b in range(n_batches):
        total_inside += estimate_pi_batch(points_per_batch, seed + b)
    total_points = n_batches * points_per_batch
    return 4.0 * total_inside / total_points


def parallel_estimate_pi(n_batches, points_per_batch, seed, n_jobs):
    """TODO: реализовать через joblib.Parallel(n_jobs=n_jobs)(delayed(...)(...) ...),
    просуммировать результаты батчей аналогично sequential_estimate_pi()."""
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    args = parser.parse_args()

    n_batches, points_per_batch, seed = variant_params(args.variant)
    print(f"Вариант {args.variant}: n_batches={n_batches}, points_per_batch={points_per_batch}, seed={seed}")

    t0 = time.perf_counter()
    pi_estimate = sequential_estimate_pi(n_batches, points_per_batch, seed)
    t1 = time.perf_counter()
    print(f"Pi ~= {pi_estimate:.5f}, последовательно за {t1 - t0:.3f} с")

    print("Далее реализуйте parallel_estimate_pi() на joblib и замерьте время")
    print("при n_jobs = 1, 2, 4, -1; постройте таблицу/график speedup.")


if __name__ == "__main__":
    main()
