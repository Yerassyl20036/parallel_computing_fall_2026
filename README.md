# Parallel Computing — Лабораторные работы

Курс: «Параллельные и распределённые вычисления в научных и прикладных задачах».
Магистратура, AIU. Автор: **Ерасыл Маратов**, вариант **5**.

Каждой неделе соответствует отдельная папка `weekN/` с реализацией и отчётом.

| Неделя | Тема | Статус |
|---:|---|---|
| 1 | Профилирование последовательного Python-кода | готово |
| 2 | threading vs multiprocessing (GIL) | готово |
| 3 | joblib + Monte-Carlo | — |
| 4 | Векторизация | — |
| 5 | Dask | — |
| 6 | Ray | — |
| 7 | MPI | — |
| 9 | OpenMP | — |
| 10 | CuPy | — |
| 11 | JAX | — |
| 12 | Bayesian MCMC | — |
| 13 | Scaling | — |
| 14 | SLURM / reproducibility | — |

Исходные материалы курса (`Методические_указания_к_лабораторным.pdf`,
`Образец_отчёта_Лабораторная_1 (1).docx`, `course_materials_starter_code.zip`,
`Лекция_1_...`) лежат в корне репозитория.

## Параметры варианта 5

| Неделя | Параметры |
|---:|---|
| 1 | N = 460, D = 4, seed = 1185 |
| 2 | cpu_n = 280 000, io_sleep = 0.40 с |

(Параметры дальнейших недель — по мере выполнения работ.)

## Как воспроизвести

```bash
python3 -m pip install --user numpy scipy line_profiler memory_profiler
export PATH="$HOME/Library/Python/3.14/bin:$PATH"   # для kernprof / mprof

cd week1
python3 starter.py --variant 5
python3 -m cProfile -s cumulative starter.py --variant 5
kernprof -l -v starter_profiled.py --variant 5
python3 -m memory_profiler starter_profiled.py --variant 5
python3 bonus_numpy.py --variant 5
```
