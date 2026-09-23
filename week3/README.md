# Неделя 3. joblib.Parallel + Монте-Карло оценка Pi

**Вариант 5:** n_batches = 13, points_per_batch = 900 000, seed = 2065.
**Оборудование замера:** Apple M1 Pro (10 логических ядер), macOS, Python 3.14, joblib 1.6.0 (backend `loky`).

## Содержимое

| Файл | Что это |
|---|---|
| `starter.py` | Оригинальный стартовый код (без изменений). |
| `solution.py` | Реализация `parallel_estimate_pi()` через `joblib.Parallel`/`delayed` + benchmark-харнесс. |
| `plot_speedup.py` | Строит `results/speedup.png` из `results/bench.json`. |
| `results/bench.json` | Сырые замеры (min/median/samples для sequential и n_jobs ∈ {1, 2, 4, -1}). |
| `results/bench_stdout.txt` | Консольный вывод замера. |
| `results/speedup.png` | График speedup(n_jobs). |
| `REPORT.md` | Полный markdown-отчёт. |

## Как воспроизвести

```bash
python3 solution.py --variant 5 --benchmark --repeats 3 --out results/bench.json
python3 plot_speedup.py
```

## Ключевой результат

| n_jobs | Время (мин, с) | Speedup vs sequential |
|---:|---:|---:|
| sequential | 2,800 | 1,00× |
| 1 | 2,784 | 1,01× |
| 2 | 1,530 | 1,83× |
| 4 | 0,893 | **3,14×** |
| -1 (=10) | 0,482 | **5,81×** |

Оценка Pi одинакова для всех конфигураций (`Pi ≈ 3,14154`) — редукция бит-в-бит совпадает с последовательной, потому что каждый батч получает свой детерминированный `seed + b` и суммирование ассоциативно на целых.

Подробнее — в `REPORT.md`.
