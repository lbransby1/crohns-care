import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from app.schemas import DayHistory


def build_hbi_chart(history: list[DayHistory]) -> bytes:
    df = pd.DataFrame([d.model_dump() for d in history])
    n = len(df)
    roll = 7 if n >= 45 else 3
    df["hbi_rolling"] = df["hbi"].rolling(window=roll, min_periods=1, center=True).mean()

    plt.figure(figsize=(9.5, 3.2), dpi=200)
    ax = plt.subplot(111)

    ax.axhspan(0, 4.9, color="#e8f5e9", alpha=0.75, label="Remission (<5)")
    ax.axhspan(5, 7.9, color="#fff9c4", alpha=0.75, label="Mild (5-7)")
    ax.axhspan(8, max(df["hbi"].max() + 2, 14), color="#ffebee", alpha=0.75, label="Moderate/Severe (8+)")

    marker_size = 2.2 if n >= 45 else 3.5
    ax.plot(
        df["day"],
        df["hbi"],
        marker="o",
        markersize=marker_size,
        color="#90caf9",
        linestyle=":",
        alpha=0.6,
        label="Daily HBI",
    )
    ax.plot(
        df["day"],
        df["hbi_rolling"],
        color="#1565c0",
        linewidth=2.2,
        label=f"{roll}-Day Rolling Trend",
    )

    ax.set_title("Longitudinal Harvey-Bradshaw Index (HBI) Trajectory", fontsize=9, fontweight="bold", pad=8)
    ax.set_xlabel("Monitoring Day", fontsize=8)
    ax.set_ylabel("HBI Score", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    if n <= 21:
        ax.set_xticks(df["day"])
    else:
        step = 7 if n <= 60 else 10
        ticks = list(range(1, n + 1, step))
        if ticks[-1] != n:
            ticks.append(int(n))
        ax.set_xticks(ticks)
    ax.tick_params(labelsize=7)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=7)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    buf = io.BytesIO()
    try:
        plt.savefig(buf, format="png", bbox_inches="tight")
    finally:
        plt.close("all")
    buf.seek(0)
    return buf.read()
