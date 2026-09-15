"""
Лабораторная работа 2. threading vs multiprocessing, эффект GIL.

В этом задании даны ДВЕ учебные нагрузки:
  - cpu_bound_task(n)  — чисто вычислительная задача (проверка чисел на простоту);
  - io_bound_task(sec) — имитация задачи ввода-вывода (time.sleep, как заглушка
    сетевого запроса/чтения диска).

Ваша задача — используя threading.Thread и multiprocessing.Process,
запустить каждую нагрузку в 1 / 2 / 4 потоках (или процессах) и
экспериментально показать:
  1) что threading НЕ ускоряет cpu_bound_task (из-за GIL);
  2) что threading ускоряет io_bound_task (GIL освобождается на I/O);
  3) что multiprocessing ускоряет cpu_bound_task.

Заполните функции run_with_threads() и run_with_processes() и таблицу
результатов в отчёте (время при 1/2/4 воркерах для каждой комбинации).

Запуск:
    python starter.py --variant <номер_варианта>
"""
import argparse
import threading
import multiprocessing
import time


def variant_params(variant: int):
    variant = ((variant - 1) % 15) + 1
    n_tasks = 4  # количество параллельных задач для запуска (фиксировано для сравнимости)
    cpu_n = 200_000 + (variant - 1) * 20_000   # верхняя граница поиска простых чисел
    io_sleep = 0.3 + 0.02 * variant            # имитация задержки I/O, сек
    return n_tasks, cpu_n, io_sleep


def is_prime(x):
    if x < 2:
        return False
    for d in range(2, int(x ** 0.5) + 1):
        if x % d == 0:
            return False
    return True


def cpu_bound_task(n):
    """Считает количество простых чисел до n — чисто вычислительная нагрузка."""
    count = sum(1 for x in range(2, n) if is_prime(x))
    return count


def io_bound_task(sec):
    """Имитация задачи ввода-вывода."""
    time.sleep(sec)
    return sec


def run_sequential(task_fn, arg, n_tasks):
    t0 = time.perf_counter()
    for _ in range(n_tasks):
        task_fn(arg)
    return time.perf_counter() - t0


def run_with_threads(task_fn, arg, n_tasks, n_workers):
    """TODO: реализовать запуск n_tasks вызовов task_fn(arg) на n_workers потоках
    (threading.Thread) и вернуть время выполнения."""
    raise NotImplementedError


def run_with_processes(task_fn, arg, n_tasks, n_workers):
    """TODO: реализовать запуск n_tasks вызовов task_fn(arg) на n_workers процессах
    (multiprocessing.Process или Pool) и вернуть время выполнения."""
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, required=True)
    args = parser.parse_args()

    n_tasks, cpu_n, io_sleep = variant_params(args.variant)
    print(f"Вариант {args.variant}: n_tasks={n_tasks}, cpu_n={cpu_n}, io_sleep={io_sleep:.2f}с")

    t_seq_cpu = run_sequential(cpu_bound_task, cpu_n, n_tasks)
    print(f"CPU-bound, последовательно: {t_seq_cpu:.3f} с")

    t_seq_io = run_sequential(io_bound_task, io_sleep, n_tasks)
    print(f"I/O-bound, последовательно: {t_seq_io:.3f} с")

    print("Далее реализуйте run_with_threads()/run_with_processes() и заполните")
    print("таблицу результатов в отчёте для 1/2/4 воркеров по обеим нагрузкам.")


if __name__ == "__main__":
    main()
