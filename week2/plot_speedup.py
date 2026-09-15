"""Строит график speedup(n_workers) для 4 комбинаций (threads/CPU, threads/IO,
processes/CPU, processes/IO) по данным results/bench.json."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
data = json.loads((HERE / "results" / "bench.json").read_text())

workers = [1, 2, 4]

fig, ax = plt.subplots(figsize=(7, 5))

styles = {
    ("cpu_bound", "threads"):   dict(color="tab:red",    marker="o", linestyle="-",  label="threads / CPU"),
    ("cpu_bound", "processes"): dict(color="tab:red",    marker="s", linestyle="--", label="processes / CPU"),
    ("io_bound",  "threads"):   dict(color="tab:blue",   marker="o", linestyle="-",  label="threads / IO"),
    ("io_bound",  "processes"): dict(color="tab:blue",   marker="s", linestyle="--", label="processes / IO"),
}

for wname in ("cpu_bound", "io_bound"):
    seq = data["data"][wname]["sequential"]["min"]
    for mode in ("threads", "processes"):
        speedups = [seq / data["data"][wname][mode][str(w)]["min"] for w in workers]
        ax.plot(workers, speedups, **styles[(wname, mode)])

ax.plot(workers, workers, color="gray", linestyle=":", label="ideal (=n)")

ax.set_xticks(workers)
ax.set_xlabel("n_workers")
ax.set_ylabel("speedup vs sequential")
ax.set_title(f"Variant {data['variant']}: threading vs multiprocessing "
             f"(cpu_n={data['cpu_n']}, io_sleep={data['io_sleep']:.2f} с, "
             f"n_tasks={data['n_tasks']})")
ax.grid(True, alpha=0.3)
ax.legend(loc="best")
fig.tight_layout()
out = HERE / "results" / "speedup.png"
fig.savefig(out, dpi=140)
print(f"Wrote {out}")
