"""Task 4 - Trend Analysis by Release Year."""
import matplotlib.pyplot as plt

from common import RED, TYPE_COLORS, load_clean, save_fig, write_text


def main():
    df = load_clean()
    yearly = df.groupby("release_year").size()                       # Steps 1-2
    by_type = df.groupby(["release_year", "type"]).size().unstack(fill_value=0)
    growth = yearly.pct_change() * 100                               # Step 3
    last_year = int(yearly.index.max())
    peak_year = int(yearly.idxmax())

    recent = yearly[yearly.index >= 2000]                            # Step 4
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(recent.index, recent.values, color=RED, marker="o", lw=2)
    ax.axvline(peak_year, color="grey", ls="--", lw=1)
    ax.annotate(f"Peak: {peak_year} ({yearly[peak_year]:,})", (peak_year, yearly[peak_year]),
                xytext=(-110, -5), textcoords="offset points", arrowprops={"arrowstyle": "->"})
    ax.set_title("Titles released per year (2000+)")
    ax.set_xlabel("Release year")
    ax.set_ylabel("Titles")
    save_fig(fig, "task4_yearly_releases.png")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for t in by_type.columns:
        s = by_type.loc[by_type.index >= 2000, t]
        ax.plot(s.index, s.values, marker="o", lw=2, label=t, color=TYPE_COLORS[t])
    ax.set_title("Movies vs TV Shows released per year (2000+)")
    ax.set_xlabel("Release year")
    ax.set_ylabel("Titles")
    ax.legend()
    save_fig(fig, "task4_trend_by_type.png")

    g = growth[(growth.index >= 2005) & (growth.index < last_year)]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(g.index, g.values, color=[RED if v >= 0 else "#555555" for v in g.values])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title("Year-over-year change in titles released (%)")
    ax.set_xlabel("Release year")
    ax.set_ylabel("% change")
    save_fig(fig, "task4_yoy_growth.png")

    added = df["year_added"].value_counts().sort_index()
    added = added[added.index >= 2012]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(added.index.astype(int), added.values, color=RED)
    ax.set_title("Titles added to Netflix per year")
    ax.set_xlabel("Year added")
    ax.set_ylabel("Titles")
    save_fig(fig, "task4_titles_added_per_year.png")

    # Step 5 - interpretation
    decades = yearly.groupby((yearly.index // 10) * 10).sum()
    decades.index = [f"{d}s" for d in decades.index]
    lag = (df["year_added"] - df["release_year"]).dropna()
    since_2015 = yearly[yearly.index >= 2015].sum() / yearly.sum() * 100
    after_peak = yearly[yearly.index > peak_year]
    added_peak = int(added.idxmax())
    text = f"""TASK 4 - TREND ANALYSIS BY RELEASE YEAR
{'=' * 40}
Release years covered: {int(yearly.index.min())} - {last_year}
Peak release year: {peak_year} with {yearly[peak_year]:,} titles
Titles released in 2010: {yearly.get(2010, 0):,}  ->  in {peak_year}: {yearly[peak_year]:,}
Peak year for titles ADDED to Netflix: {added_peak} ({added.max():,} titles)

Titles by decade of release:
{decades.to_string()}

INTERPRETATION
- {since_2015:.0f}% of the catalog was released in 2015 or later: this is a recent-content library.
- Releases grew strongly through the 2010s and peaked in {peak_year}.
- After the peak: {', '.join(f'{int(y)}: {v:,}' for y, v in after_peak.items())}.
  The latest year ({last_year}) may be incomplete, since the data is a snapshot, so treat the drop with caution.
- Typical lag between release and arrival on Netflix: median {lag.median():.0f} year(s);
  {(lag <= 1).mean() * 100:.0f}% of titles were added within a year of release.
- Older titles (before 2000) are a small back-catalog: {yearly[yearly.index < 2000].sum():,} titles.
"""
    write_text("task4_summary.txt", text)


if __name__ == "__main__":
    main()
