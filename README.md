# Netflix Data Analysis using Python

Auspify Technologies internship project - Data Analysis using Python. All 6 tasks are completed
from `Dataset.csv` (8,790 titles).

## Tasks completed
| Task | Script | Main outputs |
|---|---|---|
| 1. Data Cleaning & Preparation | `task1_cleaning.py` | `data/cleaned_netflix.csv`, `output/task1_cleaning_log.txt` |
| 2. Content Type Analysis Dashboard | `task2_content_type.py` | 2 charts, `task2_summary.txt` |
| 3. Country-Wise Content Analysis | `task3_country.py` | 2 charts, ranking CSV, `task3_summary.txt` |
| 4. Trend Analysis by Release Year | `task4_trends.py` | 4 charts, `task4_summary.txt` |
| 5. Content Rating & Genre Analysis | `task5_rating_genre.py` | 4 charts, 2 interactive HTML charts, `task5_summary.txt` |
| 6. Business Insights Report | `task6_business_report.py` | 2 dashboards, `task6_business_report.md` |

## How to run
```bash
pip install -r requirements.txt
python run_all.py          # runs all 6 tasks in order
# or run one task:  python task1_cleaning.py   (Task 1 must run first)
```
Charts are saved in `output/charts/`, reports in `output/`.

## Project structure
```
data/      Dataset.csv (raw) and cleaned_netflix.csv (created by Task 1)
output/    charts, summaries, interactive HTML, final report
common.py  shared paths, styling and helper functions
```

## Cleaning steps (Task 1)
Trim whitespace, handle missing values (filled with "Not Given"), remove duplicate rows
(including repeated titles with different IDs), standardize Type, Rating and Country,
parse dates, split duration into value and unit, and add an audience `rating_group` column.

## Tools
Python, pandas, matplotlib, seaborn, plotly.
