"""Shared paths, plotting style and helper functions used by every task script."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save charts to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "output"
CHARTS = OUT / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

RAW = DATA / "Dataset.csv"
CLEAN = DATA / "cleaned_netflix.csv"

RED, DARK, GREY = "#E50914", "#221F1F", "#B3B3B3"
TYPE_COLORS = {"Movie": RED, "TV Show": DARK}
sns.set_theme(style="whitegrid")


def load_clean() -> pd.DataFrame:
    """Load the cleaned dataset produced by task1_cleaning.py."""
    if not CLEAN.exists():
        raise SystemExit("cleaned_netflix.csv not found - run task1_cleaning.py first.")
    return pd.read_csv(CLEAN, parse_dates=["date_added"])


def explode_column(df: pd.DataFrame, column: str, new_name: str, sep: str = ",") -> pd.DataFrame:
    """One row per value for comma-separated columns (countries, genres)."""
    out = df.assign(**{new_name: df[column].str.split(sep)}).explode(new_name)
    out[new_name] = out[new_name].str.strip()
    return out[out[new_name].ne("") & out[new_name].ne("Not Given")]


def save_fig(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart saved: output/charts/{name}")


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")
    print(f"  file saved: output/{name}")


def md_table(df: pd.DataFrame) -> str:
    """Tiny markdown table builder (avoids needing the tabulate package)."""
    cols = [df.index.name or ""] + list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row.values]) + " |")
    return "\n".join(lines)
