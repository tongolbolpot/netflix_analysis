"""Task 6 - Netflix Business Insights Report (EDA + dashboards + written report)."""
import matplotlib.pyplot as plt
import pandas as pd

from common import DARK, RED, TYPE_COLORS, explode_column, load_clean, md_table, save_fig, write_text

ORDER = ["Kids", "Older Kids", "Teens", "Adults", "Not Rated"]


def dashboard_overview(df, countries):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    t = df["type"].value_counts()
    _, _, pcts = axes[0, 0].pie(t.values, labels=t.index, colors=[TYPE_COLORS[i] for i in t.index],
                                autopct="%1.1f%%", startangle=90)
    for p in pcts:
        p.set_color("white")
        p.set_weight("bold")
    axes[0, 0].set_title("Content type")
    top = countries.value_counts().head(8)
    axes[0, 1].barh(top.index[::-1], top.values[::-1], color=RED)
    axes[0, 1].set_title("Top 8 countries")
    yearly = df[df["release_year"] >= 2000].groupby("release_year").size()
    axes[1, 0].plot(yearly.index, yearly.values, color=RED, lw=2, marker="o")
    axes[1, 0].set_title("Titles released per year (2000+)")
    r = df["rating"].value_counts().head(8)
    axes[1, 1].bar(r.index, r.values, color=RED)
    axes[1, 1].set_title("Top ratings")
    plt.setp(axes[1, 1].get_xticklabels(), rotation=30)
    fig.suptitle("Netflix Catalog - Overview Dashboard", fontsize=16, weight="bold")
    save_fig(fig, "task6_dashboard_overview.png")


def dashboard_content(df, genres):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    g = genres["genre"].value_counts().head(10)
    axes[0, 0].barh(g.index[::-1], g.values[::-1], color=RED)
    axes[0, 0].set_title("Top 10 genres")
    aud = df.groupby(["type", "rating_group"]).size().unstack(fill_value=0)
    aud = aud[[c for c in ORDER if c in aud.columns]]
    (aud.div(aud.sum(axis=1), axis=0) * 100).T.plot(kind="bar", ax=axes[0, 1],
                                                   color=[TYPE_COLORS[c] for c in aud.index])
    axes[0, 1].set_title("Audience group mix by type (%)")
    axes[0, 1].set_xlabel("")
    plt.setp(axes[0, 1].get_xticklabels(), rotation=0)
    axes[1, 0].hist(df.loc[df["type"] == "Movie", "duration_value"].dropna(), bins=30, color=RED)
    axes[1, 0].set_title("Movie length (minutes)")
    s = df.loc[df["type"] == "TV Show", "duration_value"].value_counts().sort_index()
    axes[1, 1].bar(s.index.astype(int).astype(str), s.values, color=DARK)
    axes[1, 1].set_title("TV shows by number of seasons")
    fig.suptitle("Netflix Catalog - Content Mix Dashboard", fontsize=16, weight="bold")
    save_fig(fig, "task6_dashboard_content.png")



def main():
    df = load_clean()                                                      # Step 1 (EDA)
    countries = explode_column(df, "country", "c")["c"]
    genres = explode_column(df, "listed_in", "genre")

    dashboard_overview(df, countries)                                      # Step 3
    dashboard_content(df, genres)

    # Step 2 - patterns
    n = len(df)
    type_pct = df["type"].value_counts(normalize=True) * 100
    top_c = countries.value_counts()
    top_g = genres["genre"].value_counts()
    yearly = df.groupby("release_year").size()
    peak = int(yearly.idxmax())
    recent_share = (df["release_year"] >= 2015).mean() * 100
    kids = (df["rating_group"] == "Kids").mean() * 100
    mature = df["rating_group"].isin(["Teens", "Adults"]).mean() * 100
    unknown_country = (df["country"] == "Not Given").mean() * 100
    unknown_director = (df["director"] == "Not Given").mean() * 100
    movie_len = df.loc[df["type"] == "Movie", "duration_value"].median()
    one_season = (df.loc[df["type"] == "TV Show", "duration_value"] == 1).mean() * 100
    lag = (df["year_added"] - df["release_year"]).dropna().median()

    kpis = pd.DataFrame({"value": [f"{n:,}", f"{type_pct['Movie']:.1f}%", f"{type_pct['TV Show']:.1f}%",
                                   top_c.size, top_g.size, f"{recent_share:.0f}%"]},
                        index=["Total titles", "Movies", "TV Shows", "Countries", "Distinct genres",
                               "Released 2015 or later"])
    kpis.index.name = "KPI"
    top_c_tbl = pd.DataFrame({"titles": top_c.head(5), "share": (top_c.head(5) / len(countries) * 100).round(1).astype(str) + "%"})
    top_c_tbl.index.name = "Country"
    top_g_tbl = pd.DataFrame({"titles": top_g.head(5)})
    top_g_tbl.index.name = "Genre"

    report = f"""# Netflix Business Insights Report

*Source: Dataset.csv, cleaned with `task1_cleaning.py`. All figures below are calculated from the data.*

## 1. Executive summary
The catalog holds **{n:,} titles**: {type_pct['Movie']:.0f}% movies and {type_pct['TV Show']:.0f}% TV shows, from
{top_c.size} countries. It is a recent library ({recent_share:.0f}% released in 2015 or later), heavily
weighted to {top_c.index[0]} content and to Teen/Adult audiences. Kids content is only {kids:.0f}% of titles.

## 2. Key metrics
{md_table(kpis)}

## 3. Key patterns
**Where content comes from**

{md_table(top_c_tbl)}

**Most common genres** (titles can carry several genres)

{md_table(top_g_tbl)}

**Trends.** Releases peak in {peak} ({yearly[peak]:,} titles). Titles typically reach Netflix about
{lag:.0f} year(s) after release. The most recent year in the data may be incomplete.

**Format.** Median movie length is {movie_len:.0f} minutes, and {one_season:.0f}% of TV shows have just one season.

## 4. Dashboards
![Overview](charts/task6_dashboard_overview.png)
![Content mix](charts/task6_dashboard_content.png)

## 5. Actionable insights
1. **Grow serialized content.** TV shows are only {type_pct['TV Show']:.0f}% of the catalog and {one_season:.0f}% of them stop
   after one season. Renewing or extending successful series would deepen the TV side of the library.
2. **Invest in underrepresented markets.** {top_c.index[0]} alone supplies {top_c.iloc[0] / len(countries) * 100:.0f}% of country credits,
   and the top 3 countries about {top_c.head(3).sum() / len(countries) * 100:.0f}%. Local content in the long tail of
   {top_c.size - 3} other countries is a diversification opportunity.
3. **Expand family and kids content.** Only {kids:.0f}% of titles are rated for kids versus {mature:.0f}% for Teens or Adults,
   so family viewing is a clear gap.
4. **Double down on proven genres.** {top_g.index[0]}, {top_g.index[1]} and {top_g.index[2]} lead the catalog and
   can anchor new releases and recommendations.
5. **Fix metadata gaps.** Country is missing for {unknown_country:.0f}% of titles and director for {unknown_director:.0f}%.
   Better metadata would make future analysis and search more reliable.

## 6. Limitations
The dataset describes the catalog only. It has no viewing, revenue or audience-score data, so these insights show
what Netflix offers, not how well it performs. Genres and countries are counted per label, so totals overlap.
"""
    write_text("task6_business_report.md", report)                         # Steps 4-5


if __name__ == "__main__":
    main()
