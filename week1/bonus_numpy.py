"""
Бонус (п. 5 порядка выполнения): векторизованная версия
compute_pairwise_distances на NumPy / SciPy и сравнение "было / стало".

Логика baseline не меняется; здесь только измеряем и сверяем результат.

Запуск:
    python bonus_numpy.py --variant 5
"""
import argparse
import statistics
import time

import numpy as np
from scipy.spatial.distance import cdist

from starter import compute_pairwise_distances, generate_points, variant_params


def compute_pairwise_distances_numpy(points_arr):
    diff = points_arr[:, None, :] - points_arr[None, :, :]
    return np.sqrt((diff * diff).sum(axis=-1))


def compute_pairwise_distances_scipy(points_arr):
    return cdist(points_arr, points_arr, metric="euclidean")


def time_it(fn, arg, repeats=5):
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn(arg)
        samples.append(time.perf_counter() - t0)
    return result, min(samples), statistics.median(samples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    n_points, dim, seed = variant_params(args.variant)
    print(f"Вариант {args.variant}: N={n_points} точек, размерность={dim}, seed={seed}")

    points = generate_points(n_points, dim, seed)
    points_arr = np.asarray(points, dtype=np.float64)

    base_result, base_min, base_med = time_it(
        compute_pairwise_distances, points, repeats=args.repeats
    )
    base_arr = np.asarray(base_result)

    np_result, np_min, np_med = time_it(
        compute_pairwise_distances_numpy, points_arr, repeats=args.repeats
    )
    sp_result, sp_min, sp_med = time_it(
        compute_pairwise_distances_scipy, points_arr, repeats=args.repeats
    )

    print()
    print(f"{'реализация':<32}{'min, с':>12}{'median, с':>14}{'speedup':>12}")
    print("-" * 70)
    print(f"{'чистый Python (baseline)':<32}{base_min:>12.4f}{base_med:>14.4f}{1.0:>12.2f}x")
    print(f"{'NumPy (broadcasting)':<32}{np_min:>12.4f}{np_med:>14.4f}{base_min / np_min:>12.2f}x")
    print(f"{'SciPy cdist':<32}{sp_min:>12.4f}{sp_med:>14.4f}{base_min / sp_min:>12.2f}x")
    print()

    print(f"NumPy  vs baseline: allclose = {np.allclose(base_arr, np_result)}")
    print(f"SciPy  vs baseline: allclose = {np.allclose(base_arr, sp_result)}")


if __name__ == "__main__":
    main()
