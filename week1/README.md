# Неделя 1. Профилирование последовательного Python-кода

**Вариант 5:** N = 460 точек, размерность = 4, seed = 1185.

## Содержимое

| Файл | Что это |
|---|---|
| `starter.py` | Оригинальный стартовый код (без изменений). |
| `starter_profiled.py` | Копия с декоратором `@profile` на `compute_pairwise_distances` — для `kernprof`/`memory_profiler`. |
| `bonus_numpy.py` | Ускоренные версии (NumPy broadcasting и `scipy.cdist`) + сверка с baseline. |
| `profiling_outputs/` | Сохранённые выводы всех запусков. |
| `REPORT.md` | Заполненный отчёт (по единой структуре из методических указаний, п. «Структура отчёта»). |

## Как запустить (сокращённо)

```bash
python3 starter.py --variant 5
python3 -m cProfile -s cumulative starter.py --variant 5
kernprof -l -v starter_profiled.py --variant 5
python3 -m memory_profiler starter_profiled.py --variant 5
python3 bonus_numpy.py --variant 5
```

`kernprof` и `mprof` устанавливаются вместе с `pip install line_profiler memory_profiler`
и попадают в `~/Library/Python/<ver>/bin/` — при необходимости добавить в `PATH`.

## Краткий вывод

- `compute_pairwise_distances()` — ~**90 %** общего времени программы (`cProfile`).
- Внутри функции ~**76 %** времени — три строки внутреннего `k`-цикла (индексация `points[i][k]`, вычитание, накопление `s`).
- `math.sqrt`/`len` — ~7–8 % каждая, `dist`-аллокация — <1 %.
- Удвоение N (460 → 920) даёт ×**4.0** замедление — подтверждает O(N²·D).
- Векторизация (`scipy.cdist`) даёт **≈ 226×** ускорения, при этом `np.allclose(base, cdist) = True`.

Подробнее — в `REPORT.md`.
