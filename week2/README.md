# Неделя 2. threading vs multiprocessing (эффект GIL)

**Вариант 5:** n_tasks = 4, cpu_n = 280 000, io_sleep = 0,40 с.
**Оборудование замера:** Apple M1 Pro (10 логических ядер), macOS, Python 3.14.

## Содержимое

| Файл | Что это |
|---|---|
| `starter.py` | Оригинальный стартовый код (без изменений). |
| `solution.py` | Реализация `run_with_threads`/`run_with_processes` + benchmark-харнесс. |
| `plot_speedup.py` | Строит `results/speedup.png` из `results/bench.json`. |
| `results/bench.json` | Сырые замеры (min/median/samples). |
| `results/bench_stdout.txt` | Консольный вывод замера. |
| `results/speedup.png` | График speedup для 4 комбинаций. |
| `REPORT.md` | Полный markdown-отчёт. |
| `Отчёт_Лабораторная_2_вариант5.docx` | Отчёт в docx по шаблону преподавателя. |

## Как воспроизвести

```bash
python3 solution.py --variant 5 --benchmark --repeats 3 --out results/bench.json
python3 plot_speedup.py
```

## Ключевой результат

| Комбинация | speedup при 4 воркерах | вывод |
|---|---:|---|
| threads / CPU | 1,00× | GIL не даёт ускорения |
| processes / CPU | 3,43× | реальный CPU-параллелизм |
| threads / IO | 4,01× | идеальная линейная масштабируемость |
| processes / IO | 3,35× | масштабируется, но хуже потоков (оверхед `spawn`) |

Подробнее — в `REPORT.md`.
