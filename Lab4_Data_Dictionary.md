# NBA Draft Combine: Data Dictionary

Every measurement is in inches, pounds, or seconds. Missing values are the literal text `NA`, never an empty cell.

| Column | Meaning | Notes |
|---|---|---|
| `YEAR` | Combine year | 2000-2026 |
| `PLAYER` | Player name, written "Last, First" | Any join to another source must reconcile the name order |
| `POS` | Position as listed at the combine | 13 codes; dual codes like `PF-C` need a primary-position rule before any group comparison |
| `HGT` | Height without shoes (inches) | 75.75 means 6 ft 3.75 in |
| `WGT` | Weight (pounds) | One row at 0 (not a real measurement) |
| `BMI` | Body mass index, 703 x weight / height squared | Derived from `HGT` and `WGT` |
| `BF` | Body fat as a fraction of body weight | 0.067 means 6.7%; absent 2000, 2002, 2005, and every year from 2023 |
| `WNGSPN` | Wingspan (inches) | |
| `STNDRCH` | Standing reach (inches) | |
| `HANDL` | Hand length (inches) | 2010-2025 only |
| `HANDW` | Hand width (inches) | 2010-2025 only; stored to one decimal, except 26 rows in 2024 stored as whole inches |
| `STNDVERT` | Standing vertical leap, no step (inches) | Some players skip the athletic tests; about one row in nine is `NA` |
| `LPVERT` | Maximum vertical leap, with an approach (inches) | Same coverage as `STNDVERT` |
| `LANE` | Lane agility drill time (seconds) | Lower is better |
| `SHUTTLE` | Shuttle run time (seconds) | Lower is better; 2013 on, and only a third of 2023 |
| `SPRINT` | Three-quarter-court sprint time (seconds) | Lower is better |
| `BENCH` | Bench press, repetitions at 185 lb | Absent 2014, 2016, and every year from 2020; 39 zeros are real results |
| `BAR` | Wingspan divided by height | **Stored as text** with a `%` sign, e.g. `105.9%`; must be converted before any calculation |
| `PAN` | Hand length x hand width (square inches) | 2010-2025 only |
| `PBHGT` | Standing reach + standing vertical: the height the player touches on a standing jump (inches) | |
| `PDHGT` | Standing reach + maximum vertical: the height the player touches on a running jump (inches) | |

**Source:** https://www.kaggle.com/datasets/marcusfern/nba-draft-combine (CC BY 4.0). Attribute the dataset by name and link wherever you use the data.
