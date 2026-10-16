"""Task 5 - Content Rating & Genre Analysis (with interactive Plotly charts)."""
import matplotlib.pyplot as plt
import seaborn as sns

from common import OUT, RED, explode_column, load_clean, save_fig, write_text


def interactive_charts(df, genres):
    try:
        import plotly.express as px
    except ImportError:
        print("  plotly not installed - skipping interactive charts (pip install plotly)")
        return
    fig = px.sunburst(df, path=["type", "rating_group", "rating"],
                      title="Audience targeting: type > audience group > rating",
                      color_discrete_sequence=["#E50914", "#221F1F", "#831010", "#B3B3B3", "#F5C518"])
    fig.write_html(OUT / "interactive_rating_sunburst.html", include_plotlyjs=True)
    top = genres["genre"].value_counts().head(15).index
    g = genres[genres["genre"].isin(top)].groupby(["genre", "type"]).size().reset_index(name="titles")
    fig = px.bar(g, x="titles", y="genre", color="type", orientation="h", barmode="stack",
                 category_orders={"genre": list(top)[::-1]},
                 color_discrete_map={"Movie": "#E50914", "TV Show": "#221F1F"},
                 title="Top 15 genres (hover for counts)")
    fig.write_html(OUT / "interactive_genres.html", include_plotlyjs=True)
    print("  interactive charts saved: output/interactive_*.html")


def main():
    df = load_clean()
    ratings = df["rating"].value_counts()                                   # Step 1
    genres = explode_column(df, "listed_in", "genre")                       # Step 2
    genre_counts = genres["genre"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(ratings.index, ratings.values, color=RED)
    ax.set_title("Titles by rating")
    ax.set_ylabel("Titles")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "task5_ratings.png")

    top15 = genre_counts.head(15)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top15.index[::-1], top15.values[::-1], color=RED)
    ax.set_title("Top 15 genres")
    ax.set_xlabel("Titles")
    save_fig(fig, "task5_top_genres.png")

    # Step 3 - ratings across content types
    cross = (df.groupby(["type", "rating"]).size().unstack(fill_value=0))
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(11, 3))
    sns.heatmap(cross_pct.round(1), annot=True, fmt=".1f", cmap="Reds", cbar_kws={"label": "% of type"}, ax=ax)
    ax.set_title("Rating mix within each content type (%)")
    ax.set_ylabel("")
    ax.set_xlabel("")
    save_fig(fig, "task5_rating_by_type_heatmap.png")

    audience = df.groupby(["type", "rating_group"]).size().unstack(fill_value=0)
    order = [c for c in ["Kids", "Older Kids", "Teens", "Adults", "Not Rated"] if c in audience.columns]
    audience_pct = audience[order].div(audience[order].sum(axis=1), axis=0) * 100

    top8 = genre_counts.head(8).index
    g8 = genres[genres["genre"].isin(top8)]
    gm = (g8.groupby(["genre", "rating_group"]).size().unstack(fill_value=0)[order])
    gm_pct = gm.div(gm.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(gm_pct.round(0), annot=True, fmt=".0f", cmap="Reds", cbar_kws={"label": "% of genre"}, ax=ax)
    ax.set_title("Audience group mix for the top 8 genres (%)")
    ax.set_ylabel("")
    ax.set_xlabel("")
    save_fig(fig, "task5_genre_audience_heatmap.png")

    interactive_charts(df, genres)                                          # Step 4

    # Step 5 - audience insights
    adult_teen = (df["rating_group"].isin(["Adults", "Teens"])).mean() * 100
    text = f"""TASK 5 - CONTENT RATING & GENRE ANALYSIS
{'=' * 40}
Most common ratings: {', '.join(f'{r} ({n:,})' for r, n in ratings.head(3).items())}
Most common genres:  {', '.join(f'{g} ({n:,})' for g, n in genre_counts.head(5).items())}

Audience group share by type (%):
{audience_pct.round(1).to_string()}

AUDIENCE INSIGHTS
- {adult_teen:.0f}% of titles are rated for Teens or Adults; Kids content is only
  {(df['rating_group'] == 'Kids').mean() * 100:.0f}% of the catalog.
- {ratings.index[0]} is the single biggest rating ({ratings.iloc[0] / len(df) * 100:.0f}% of titles).
- Movies are {audience_pct.loc['Movie', 'Adults']:.0f}% Adult-rated versus {audience_pct.loc['TV Show', 'Adults']:.0f}% for TV Shows;
  TV Shows have a larger Kids share ({audience_pct.loc['TV Show', 'Kids']:.0f}% vs {audience_pct.loc['Movie', 'Kids']:.0f}% for movies).
- Genre labels overlap, so one title counts toward each of its genres ({len(genre_counts)} distinct genres in total).
"""
    write_text("task5_summary.txt", text)


if __name__ == "__main__":
    main()
