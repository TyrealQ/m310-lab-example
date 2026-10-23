# NBA Draft Combine Scouting Brief

## Question

Are today’s NBA Draft Combine prospects more athletic than prospects from twenty years ago? The project should help a scouting director compare an individual prospect’s combine numbers with typical prospects from past classes.

## Stakeholder and use case

The stakeholder is the scouting director. The primary use case is a scouting reference that shows what a typical prospect looked like in each comparison era, with every measurement remaining interpretable in its original units. The initial comparison is pooled across all prospects; Benchmarks also gives the count and the mean max vertical by primary position in each era, to check the change in the mix of positions.

## Comparison groups

Compare two five-class eras:

- Early era: 2000–2004
- Recent era: 2022–2026

The analysis must use these year boundaries exactly. The full 2000–2026 file may be used for context or data-quality checks, but it must not change the two defined comparison groups.

## Data scope

Use only the supplied `nba_draft_combine.csv` file and `Lab4_Data_Dictionary.md`. Do not join outside data, infer draft outcomes, or add external prospect information.

Every measurement in the file is in scope, organized into these categories:

- Body size: height, weight, and BMI
- Body composition: body fat
- Length and proportions: wingspan, standing reach, hand length, hand width, wingspan-to-height ratio, and hand area
- Jumping: standing vertical, maximum vertical, standing-jump touch height, and running-jump touch height
- Agility and speed: lane agility, shuttle, and three-quarter-court sprint
- Strength: bench press repetitions

The first code in `POS` is the prepared primary-position value. It may be retained for future analysis, but the benchmarks keep all prospects together, with the table by primary position beside them.

## Data-quality and comparability requirements

- Missing values are the literal text `NA`, never empty cells. Missing values must remain missing and must not be converted to zero.
- One weight value is zero even though zero is not a real measurement. Its treatment must be documented before any derived or comparative calculation; associated BMI must not be treated as valid without resolving that record.
- `BAR` is stored as text with a percent sign, such as `105.9%`, and must be converted to a numeric representation before calculation or summary.
- Body fat is absent in 2000, 2002, 2005, and every year from 2023 onward.
- Hand length and hand width are available only from 2010–2025. Hand width is stored to one decimal place except for 26 whole-inch records in 2024.
- Standing and maximum vertical results are missing for some prospects who skipped athletic tests.
- Shuttle results begin in 2013 and are available for only about one-third of 2023.
- Bench press is absent in 2014, 2016, and every year from 2020 onward; zero bench results are real results.
- Coverage must be checked separately for every measurement in both comparison eras before declaring an era comparison valid.

## Summary-statistic decision

The center used to describe a typical prospect is intentionally open until the distributions are inspected. The workbook must state which center statistic is selected for each measure, explain why it is appropriate for that distribution, and preserve the original measurement units. No combined athleticism score should be created.

## Source attribution

Attribute the source as the Kaggle dataset **NBA Draft Combine** and link to [https://www.kaggle.com/datasets/marcusfern/nba-draft-combine](https://www.kaggle.com/datasets/marcusfern/nba-draft-combine). The data dictionary identifies the source license as CC BY 4.0.
