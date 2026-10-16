"""Task 2 - Content Type Analysis Dashboard (Movies vs TV Shows)."""
import matplotlib.pyplot as plt

from common import TYPE_COLORS, load_clean, save_fig, write_text


def main():
    df = load_clean()                                   # Step 1
    counts = df["type"].value_counts()                  # Step 2
    pct = (counts / counts.sum() * 100).round(1)
    colors = [TYPE_COLORS[t] for t in counts.index]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))   # Step 3
    bars = axes[0].bar(counts.index, counts.values, color=colors)
    axes[0].bar_label(bars, labels=[f"{v:,}" for v in counts.values], padding=3)
    axes[0].set_title("Number of titles by type")
    axes[0].set_ylabel("Titles")
    _, labels, pcts = axes[1].pie(counts.values, labels=counts.index, colors=colors, autopct="%1.1f%%",
                                  startangle=90, wedgeprops={"edgecolor": "white"})
    for t in pcts:
        t.set_color("white")
        t.set_weight("bold")
    axes[1].set_title("Share of catalog")
    fig.suptitle("Netflix Content Type Distribution", fontsize=14, weight="bold")
    save_fig(fig, "task2_content_type.png")

    # Step 4 - compare proportions over time
    recent = df[df["release_year"] >= 2010]
    share = recent.groupby(["release_year", "type"]).size().unstack(fill_value=0)
    share = share.div(share.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(9, 4.5))
    share.plot(kind="bar", stacked=True, ax=ax, color=[TYPE_COLORS[c] for c in share.columns])
    ax.set_title("Movie vs TV Show share of titles by release year (2010+)")
    ax.set_ylabel("% of titles")
    ax.set_xlabel("Release year")
    ax.legend(title="")
    save_fig(fig, "task2_type_share_by_year.png")

    # Step 5 - summary
    movies = df[df["type"] == "Movie"]["duration_value"]
    shows = df[df["type"] == "TV Show"]["duration_value"]
    ratio = counts["Movie"] / counts["TV Show"]
    text = f"""TASK 2 - CONTENT TYPE ANALYSIS
{'=' * 40}
Total titles:   {len(df):,}
Movies:         {counts['Movie']:,} ({pct['Movie']}%)
TV Shows:       {counts['TV Show']:,} ({pct['TV Show']}%)
Movie : TV Show ratio = {ratio:.1f} : 1

Average movie length:        {movies.mean():.0f} minutes (median {movies.median():.0f})
Average TV show length:      {shows.mean():.1f} seasons (median {shows.median():.0f})
TV shows with a single season: {(shows == 1).mean() * 100:.0f}%

KEY FINDINGS
- Movies make up about {pct['Movie']:.0f}% of the catalog, roughly {ratio:.1f} movies for every TV show.
- Most TV shows in the catalog are short-run: {(shows == 1).mean() * 100:.0f}% have only one season.
"""
    write_text("task2_summary.txt", text)


if __name__ == "__main__":
    main()
