# Combine athleticism benchmarks

## Project
Question: Are today's prospects more athletic than those of twenty years ago?
Stakeholder: a scouting director who compares a prospect's numbers with past classes.
Groups: 2000-2004 against 2022-2026.
Shape: two groups.
Test: t-test on the max vertical (LPVERT), 2000-2004 against 2022-2026.
The full plan is in PROJECT_BRIEF.md. Read it before planning a task.

## Data
- nba_draft_combine.csv: NBA Draft Combine Measurements, 2000-2026 (Kaggle, CC BY 4.0).
  1,749 rows when downloaded, one per prospect per year.
- Lab4_Data_Dictionary.md defines every column. Read it before any task.
- Missing values are the text NA. Shuttle, bench press, body fat, and the hand
  measures are missing for whole ranges of years.

## Rules for the agent
- Never change the CSV. Build the workbook with the officecli-xlsx skill.
- Copy the CSV unchanged into a sheet named Raw; write cleaned rows to a sheet named Clean.
- Log every change in Decision_Log: what, where, rows before, rows after, rows removed, because,
  decided by ("me" for my decisions, "agent" for a decision you make).
- Every figure in Benchmarks is a formula, never a typed number.
- Ask me before dropping a row or changing a value.
- Never commit a file that `.gitignore` leaves out.

## Rules the workbook must pass
- Rows in Clean equal rows in Raw minus every removal in the log.
- No weight and no shuttle is 0.
- Every BAR_NUM value lies between 0.97 and 1.18.
- Every Clean row has a primary position and an era.
