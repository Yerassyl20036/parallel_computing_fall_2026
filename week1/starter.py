"""
Лабораторная работа 1. Профилирование последовательного Python-кода.

Задача, которую нужно профилировать, специально написана неэффективно:
она вычисляет матрицу попарных евклидовых расстояний между точками
чистыми Python-циклами (без NumPy). Ваша задача — НЕ переписывать её
с нуля, а сначала профилировать (cProfile, line_profiler, memory_profiler),
найти узкое место и обосновать его в отчёте.

Опционально (для желающих) — предложить ускоренную версию (например,
на NumPy) и сравнить время выполнения "было/стало".

Запуск:
    python starter.py --variant <номер_варианта>
"""
import argparse
import math
import random
import time


def variant_params(variant: int):
    """Параметры варианта: количество точек N и размерность пространства D."""
    variant = ((variant - 1) % 15) + 1
    seed = 1000 + variant * 37
    n_points = 300 + (variant - 1) * 40   # растёт с номером варианта: 300..860
    dim = 3 + (variant % 4)               # 3..6
    return n_points, dim, seed


def generate_points(n_points, dim, seed):
    rng = random.Random(seed)
    return [[rng.uniform(-10, 10) for _ in range(dim)] for _ in range(n_points)]


def compute_pairwise_distances(points):
    """Намеренно неэффективная реализация: чистые Python-циклы."""
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
    parser.add_argument("--variant", type=int, required=True, help="номер варианта (1-15)")
    args = parser.parse_args()

    n_points, dim, seed = variant_params(args.variant)
    print(f"Вариант {args.variant}: N={n_points} точек, размерность={dim}, seed={seed}")

    points = generate_points(n_points, dim, seed)

    t0 = time.perf_counter()
    dist = compute_pairwise_distances(points)
    t1 = time.perf_counter()

    print(f"Матрица расстояний {len(dist)}x{len(dist)} построена за {t1 - t0:.3f} с")
    print("Задание: профилируйте эту программу (cProfile / line_profiler) и найдите,")
    print("сколько времени и почему уходит именно на compute_pairwise_distances().")


if __name__ == "__main__":
    main()
