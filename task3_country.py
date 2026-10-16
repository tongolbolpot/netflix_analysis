"""Task 3 - Country-Wise Netflix Content Analysis."""
import matplotlib.pyplot as plt
import pandas as pd

from common import OUT, RED, TYPE_COLORS, explode_column, load_clean, save_fig, write_text


def main():
    df = load_clean()
    known = explode_column(df, "country", "country_single")        # Step 1: one row per country
    unknown = int((df["country"] == "Not Given").sum())

    counts = known["country_single"].value_counts()                # Step 2
    top = counts.head(10)                                          # Step 3
    ranking = pd.DataFrame({"titles": top, "share_%": (top / len(known) * 100).round(1)})
    ranking.index.name = "country"
    ranking.to_csv(OUT / "task3_country_ranking.csv")

    fig, ax = plt.subplots(figsize=(9, 5))                         # Step 4
    ax.barh(top.index[::-1], top.values[::-1], color=RED)
    for y, v in enumerate(top.values[::-1]):
        ax.text(v + counts.max() * 0.01, y, f"{v:,}", va="center")
    ax.set_title("Top 10 content-producing countries")
    ax.set_xlabel("Titles")
    save_fig(fig, "task3_top_countries.png")

    by_type = pd.crosstab(known["country_single"], known["type"]).loc[top.index]
    fig, ax = plt.subplots(figsize=(10, 5))
    by_type.plot(kind="bar", stacked=True, ax=ax, color=[TYPE_COLORS[c] for c in by_type.columns])
    ax.set_title("Top 10 countries: Movies vs TV Shows")
    ax.set_xlabel("")
    ax.set_ylabel("Titles")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(title="")
    save_fig(fig, "task3_countries_by_type.png")

    # Step 5 - insights
    tv_share = (by_type["TV Show"] / by_type.sum(axis=1) * 100).round(0)
    top3 = top.head(3)
    text = f"""TASK 3 - COUNTRY-WISE ANALYSIS
{'=' * 40}
Countries represented: {counts.size}
Titles with country listed: {len(df) - unknown:,}; country not given: {unknown:,} ({unknown / len(df) * 100:.1f}%)

TOP 10 RANKING
{ranking.to_string()}

BUSINESS INSIGHTS
- {top.index[0]} leads with {top.iloc[0]:,} titles, {top.iloc[0] / len(known) * 100:.0f}% of all country credits.
- The top 3 ({', '.join(top3.index)}) account for {top3.sum() / len(known) * 100:.0f}% of the catalog,
  so content supply is concentrated in a few markets.
- Among the top 10, {tv_share.idxmax()} has the highest TV Show share ({tv_share.max():.0f}%) and
  {tv_share.idxmin()} the lowest ({tv_share.min():.0f}%).
- {counts.size - 10} further countries share the remaining {(counts.sum() - top.sum()) / len(known) * 100:.0f}% of titles,
  a long tail of smaller markets.
"""
    write_text("task3_summary.txt", text)


if __name__ == "__main__":
    main()
