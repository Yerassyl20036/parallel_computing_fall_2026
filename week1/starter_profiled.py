"""
Копия starter.py с декоратором @profile на compute_pairwise_distances
для запуска через kernprof / line_profiler.

Использование:
    kernprof -l -v starter_profiled.py --variant 5
"""
import argparse
import math
import random
import time


def variant_params(variant: int):
    variant = ((variant - 1) % 15) + 1
    seed = 1000 + variant * 37
    n_points = 300 + (variant - 1) * 40
    dim = 3 + (variant % 4)
    return n_points, dim, seed


def generate_points(n_points, dim, seed):
    rng = random.Random(seed)
    return [[rng.uniform(-10, 10) for _ in range(dim)] for _ in range(n_points)]


@profile  # noqa: F821 — вводится kernprof-ом во время запуска
def compute_pairwise_distances(points):
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            s = 0.0
            for k in range(len(points[i])):
                diff = points[i][k] - points[j][k]
                s += diff * diff
            dist[i][j] = math.sqrt(s)
    return dist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    args = parser.parse_args()

    n_points, dim, seed = variant_params(args.variant)
    print(f"Вариант {args.variant}: N={n_points} точек, размерность={dim}, seed={seed}")

    points = generate_points(n_points, dim, seed)

    t0 = time.perf_counter()
    dist = compute_pairwise_distances(points)
    t1 = time.perf_counter()

    print(f"Матрица расстояний {len(dist)}x{len(dist)} построена за {t1 - t0:.3f} с")


if __name__ == "__main__":
    main()
