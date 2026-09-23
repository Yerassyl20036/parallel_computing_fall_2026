"""Строит график speedup(n_jobs) для joblib-версии Монте-Карло Pi
по данным results/bench.json.

Baseline: sequential_estimate_pi (без joblib). По оси X — n_jobs, при -1
подставляется реальное cpu_count из bench.json.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
data = json.loads((HERE / "results" / "bench.json").read_text())

cpu = data["cpu_count"]
seq = data["data"]["sequential"]["min"]

n_jobs_labels = [1, 2, 4, -1]
x_values = [1, 2, 4, cpu]  # -1 → cpu_count на оси

speedups = [seq / data["data"][f"n_jobs={j}"]["min"] for j in n_jobs_labels]

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(x_values, speedups, marker="o", color="tab:red", linewidth=2, label="joblib (loky)")

ideal_x = sorted(set(x_values))
ax.plot(ideal_x, ideal_x, color="gray", linestyle=":", label="ideal (=n)")

for x, y, j in zip(x_values, speedups, n_jobs_labels):
    label = f"n_jobs=-1\n(={cpu})" if j == -1 else f"n_jobs={j}"
    ax.annotate(f"{y:.2f}×", xy=(x, y), xytext=(6, 6), textcoords="offset points", fontsize=9)
    ax.annotate(label, xy=(x, 0), xytext=(0, -18), textcoords="offset points",
                ha="center", fontsize=8, color="gray")

ax.set_xticks(ideal_x)
ax.set_xlabel("effective number of workers")
ax.set_ylabel("speedup vs sequential")
ax.set_title(
    f"Variant {data['variant']}: joblib Monte-Carlo Pi "
    f"(n_batches={data['n_batches']}, points_per_batch={data['points_per_batch']:,})"
)
ax.grid(True, alpha=0.3)
ax.legend(loc="best")
ax.set_ylim(0, max(max(speedups), max(ideal_x)) * 1.1)
fig.tight_layout()
out = HERE / "results" / "speedup.png"
fig.savefig(out, dpi=140)
print(f"Wrote {out}")
