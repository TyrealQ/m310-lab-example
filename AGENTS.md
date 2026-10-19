## Project

- User question: Are today’s NBA Draft Combine prospects more athletic than prospects from twenty years ago?
- Stakeholder: a scouting director who compares an individual prospect’s numbers with past classes.
- Comparison groups: the early era is 2000–2004; the recent era is 2022–2026. Keep the initial comparison pooled across all prospects. The first code in `POS` is the prepared primary position for possible later use.

## Data

- Main file: `nba_draft_combine.csv`.
- Data dictionary: `Lab4_Data_Dictionary.md`; read it before using the CSV.
- Missing values are stored as the literal text `NA`, never as empty cells. Missing values are not zero; real zero results must remain distinguishable from missing values.
- The file contains body-size, body-composition, length/proportion, jumping, agility/speed, and strength measurements. Test coverage differs by year: body fat is absent in several years and from 2023 onward; hand measurements cover 2010–2025; shuttle begins in 2013 and is sparse in 2023; bench is absent in 2014, 2016, and from 2020 onward; and some prospects skipped athletic tests.
- One weight value is zero even though zero is not a real measurement. Resolve and document that record before using weight or BMI.
- `BAR` is text with a `%` sign and must be converted before calculation.

## Rules for the agent

- Do not run analysis before `PROJECT_BRIEF.md` and this `AGENTS.md` exist.
- Use only `nba_draft_combine.csv` and `Lab4_Data_Dictionary.md`; do not join outside data or infer draft outcomes.
- Preserve original measurement units.
- Treat literal `NA` as missing and never replace it with zero.
- Keep true zero results, including real bench-press results, distinct from missing values.
- Convert `BAR` from percentage text before calculations or summaries.
- Check and report coverage and comparability for every measurement in both comparison eras.
- Use the first `POS` code as the primary-position value, but do not perform position comparisons unless the user later authorizes them.
- Do not create a combined athleticism score. Compare measurements independently.
- Inspect each distribution before choosing its center statistic, and document the choice.
- Attribute the Kaggle source and link wherever derived results are presented.

## Rules the workbook must pass

- Compare exactly 2000–2004 against exactly 2022–2026.
- Include every measurement in the file or explicitly mark it as not comparable because of coverage.
- Report measurement coverage and comparability for both eras.
- Preserve original units and explain the selected center statistic for each measure.
- Handle the invalid zero weight explicitly and prevent it from silently producing an invalid BMI or summary.
- Handle literal `NA` explicitly and distinguish it from real zero measurements.
- Convert `BAR` before displaying or using it numerically.
- Include Kaggle `NBA Draft Combine` attribution and the source link.
- Contain no outside data, undocumented transformations, or composite athleticism score.
