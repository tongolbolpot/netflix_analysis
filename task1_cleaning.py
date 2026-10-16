"""Task 1 - Netflix Data Cleaning & Preparation.

Step 1 import -> Step 2 missing values -> Step 3 duplicates & formatting
-> Step 4 standardize Country / Rating / Type -> Step 5 export.
"""
import pandas as pd

from common import CLEAN, RAW, write_text

TEXT_COLS = ["show_id", "type", "title", "director", "country", "rating", "duration", "listed_in"]
MISSING_TOKENS = {"", "nan", "none", "null", "n/a", "na", "-"}
FILL = "Not Given"

COUNTRY_FIXES = {"USA": "United States", "US": "United States", "U.S.": "United States",
                 "UK": "United Kingdom", "U.K.": "United Kingdom"}
TYPE_FIXES = {"movie": "Movie", "movies": "Movie", "tv show": "TV Show", "tv shows": "TV Show", "tvshow": "TV Show"}
RATING_FIXES = {"UR": "NR"}  # "Unrated" and "Not Rated" mean the same thing

# Audience grouping used later in Task 5 / 6
RATING_GROUPS = {
    "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids", "G": "Kids",
    "PG": "Older Kids", "TV-PG": "Older Kids",
    "PG-13": "Teens", "TV-14": "Teens",
    "R": "Adults", "TV-MA": "Adults", "NC-17": "Adults",
    "NR": "Not Rated",
}


def clean_country(value):
    if pd.isna(value):
        return value
    parts = [COUNTRY_FIXES.get(p.strip(), p.strip()) for p in str(value).split(",") if p.strip()]
    return ", ".join(dict.fromkeys(parts)) if parts else pd.NA


def main():
    log = ["NETFLIX DATA CLEANING LOG", "=" * 40]

    # Step 1 - import
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    log.append(f"Step 1: loaded {len(df):,} rows x {df.shape[1]} columns from {RAW.name}")

    # Step 3a - formatting: trim and collapse whitespace, turn blanks into real NAs
    for col in TEXT_COLS + ["date_added", "release_year"]:
        df[col] = df[col].str.replace(r"\s+", " ", regex=True).str.strip()
        df.loc[df[col].str.lower().isin(MISSING_TOKENS), col] = pd.NA
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

    # Step 2 - missing values
    missing = df.isna().sum()
    log.append("\nStep 2: missing values before filling")
    log += [f"  {c:<14}{n:>6}" for c, n in missing.items()]
    before = len(df)
    df = df.dropna(subset=["show_id", "title", "type", "release_year"])
    log.append(f"  dropped {before - len(df)} rows missing an ID, title, type or release year")
    for col in ["director", "country", "rating", "duration", "listed_in"]:
        df[col] = df[col].fillna(FILL)
    df["release_year"] = df["release_year"].astype(int)
    log.append(f"  filled missing director/country/rating/duration/genre with '{FILL}'")

    # Step 3b - duplicates
    n = len(df)
    df = df.drop_duplicates()
    log.append(f"\nStep 3: removed {n - len(df)} exact duplicate rows")
    n = len(df)
    df = df.drop_duplicates(subset="show_id")
    log.append(f"  removed {n - len(df)} rows with a repeated show_id")
    n = len(df)
    df = df.drop_duplicates(subset=["title", "type", "release_year", "director"])
    log.append(f"  removed {n - len(df)} rows with the same title/type/year/director")

    # Step 4 - standardize
    df["type"] = df["type"].str.lower().map(TYPE_FIXES).fillna(df["type"])
    df["rating"] = df["rating"].str.upper().replace(RATING_FIXES)
    df["country"] = df["country"].map(clean_country)
    df["rating_group"] = df["rating"].map(RATING_GROUPS).fillna("Not Rated")
    log.append("\nStep 4: standardized type (Movie / TV Show), rating (upper-case, UR -> NR) and country names")
    log.append("  added rating_group column: Kids / Older Kids / Teens / Adults / Not Rated")

    # Dates and duration -> analysis-ready columns
    df["date_added"] = pd.to_datetime(df["date_added"], format="mixed", errors="coerce")
    bad_dates = int(df["date_added"].isna().sum())
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["month_added"] = df["date_added"].dt.month.astype("Int64")
    df["duration_value"] = pd.to_numeric(df["duration"].str.extract(r"(\d+)")[0], errors="coerce")
    df["duration_unit"] = df["duration"].str.extract(r"(min|Season)")[0]
    log.append(f"  parsed date_added ({bad_dates} unparseable) and split duration into value + unit")

    # Step 5 - export
    df = df.reset_index(drop=True)
    df.to_csv(CLEAN, index=False)
    log.append(f"\nStep 5: exported {len(df):,} clean rows to data/{CLEAN.name}")
    log.append("\nTop values after cleaning:")
    log.append("  type:    " + df["type"].value_counts().to_dict().__str__())
    log.append("  rating:  " + df["rating"].value_counts().to_dict().__str__())
    log.append("  country: " + df["country"].value_counts().head(5).to_dict().__str__())
    write_text("task1_cleaning_log.txt", "\n".join(log))


if __name__ == "__main__":
    main()
