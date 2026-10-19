#!/usr/bin/env python3
"""Build QIAN_LAB4.xlsx from the unchanged NBA Draft Combine CSV.

The workbook is intentionally built through OfficeCLI.  Temporary derived CSVs
are written outside the project and are removed automatically after import.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_CSV = ROOT / "nba_draft_combine.csv"
OUTPUT_XLSX = ROOT / "QIAN_LAB4.xlsx"
OFFICECLI = shutil.which("officecli") or "/Users/tyqian/.local/bin/officecli"


def run(*args: str) -> None:
    """Run one OfficeCLI command and fail immediately if it fails."""
    command = [OFFICECLI, *args]
    subprocess.run(command, cwd=ROOT, check=True)


def run_batch(operations: list[dict]) -> None:
    """Send one JSON batch to OfficeCLI, preserving cross-sheet formulas."""
    payload = json.dumps(operations)
    subprocess.run(
        [OFFICECLI, "batch", str(OUTPUT_XLSX)],
        input=payload + "\n",
        text=True,
        cwd=ROOT,
        check=True,
    )


def numeric_bar(value: str) -> str:
    """Convert BAR percentage text to a ratio string, preserving NA."""
    if value == "NA":
        return "NA"
    if not value.endswith("%"):
        raise ValueError(f"Unexpected BAR value: {value!r}")
    ratio = float(value[:-1]) / 100.0
    return f"{ratio:.6f}".rstrip("0").rstrip(".")


def primary_position(pos: str) -> str:
    """Return the first position code, or the requested missing label."""
    if pos == "NA" or not pos:
        return "none recorded"
    return pos.split("-", 1)[0]


def era_for(year: int) -> str:
    if 2000 <= year <= 2004:
        return "2000-2004"
    if 2022 <= year <= 2026:
        return "2022-2026"
    return "2005-2021"


ERA_ORDER = {"2000-2004": 0, "2005-2021": 1, "2022-2026": 2}
TARGET_ERAS = ("2000-2004", "2022-2026")
MEASURE_SPECS = (
    ("Height", "D", "HGT", "mean"),
    ("Weight", "E", "WGT", "mean"),
    ("Wingspan", "H", "WNGSPN", "mean"),
    ("Standing vertical", "L", "STNDVERT", "mean"),
    ("Max vertical", "M", "LPVERT", "mean"),
    ("Lane agility", "N", "LANE", "median"),
    ("Sprint", "P", "SPRINT", "median"),
)


def rows_for_log(rows_before: int, because: str, where: str, what: str, decided_by: str) -> list[str]:
    return [what, where, str(rows_before), str(rows_before), "0", because, decided_by]


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(SOURCE_CSV)

    with SOURCE_CSV.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        source_headers = reader.fieldnames or []
        source_rows = list(reader)

    expected_headers = [
        "YEAR", "PLAYER", "POS", "HGT", "WGT", "BMI", "BF", "WNGSPN",
        "STNDRCH", "HANDL", "HANDW", "STNDVERT", "LPVERT", "LANE",
        "SHUTTLE", "SPRINT", "BENCH", "BAR", "PAN", "PBHGT", "PDHGT",
    ]
    if source_headers != expected_headers:
        raise ValueError(f"Unexpected CSV headers: {source_headers}")
    if len(source_rows) != 1749:
        raise ValueError(f"Expected 1,749 source rows, found {len(source_rows)}")

    # Validate the explicitly retained valid zeros before building anything.
    bench_zeros = sum(float(row["BENCH"]) == 0 for row in source_rows if row["BENCH"] != "NA")
    sprint_fours = sum(float(row["SPRINT"]) == 4.0 for row in source_rows if row["SPRINT"] != "NA")
    if bench_zeros != 39:
        raise ValueError(f"Expected 39 real bench zeros, found {bench_zeros}")
    if sprint_fours != 2:
        raise ValueError(f"Expected two 4.00-second sprints, found {sprint_fours}")

    clean_headers = source_headers + ["BAR_NUM", "PRIMARY_POS", "ERA"]
    clean_rows: list[dict[str, str]] = []
    invalid_rows: dict[str, int] = {}
    danny_granger_seen = False

    for excel_row, source_row in enumerate(source_rows, start=2):
        row = dict(source_row)
        year = int(row["YEAR"])

        if row["PLAYER"] == "Dunn, Kris" and year == 2016:
            if row["WGT"] != "0.0" or row["BMI"] != "0.0":
                raise ValueError("Kris Dunn 2016 does not contain the expected zero WGT/BMI")
            row["WGT"] = "NA"
            row["BMI"] = "NA"
            invalid_rows["dunn"] = excel_row

        if row["PLAYER"] == "Beasley, Malik" and year == 2016:
            if row["SHUTTLE"] != "0.00":
                raise ValueError("Malik Beasley 2016 does not contain the expected zero SHUTTLE")
            row["SHUTTLE"] = "NA"
            invalid_rows["beasley"] = excel_row

        bar_num = numeric_bar(row["BAR"])
        row["BAR_NUM"] = bar_num
        row["PRIMARY_POS"] = primary_position(row["POS"])
        row["ERA"] = era_for(year)

        if row["PLAYER"] == "Granger, Danny" and year == 2005:
            if row["POS"] != "NA" or row["PRIMARY_POS"] != "none recorded":
                raise ValueError("Danny Granger 2005 does not match the requested missing position rule")
            danny_granger_seen = True

        clean_rows.append(row)

    if len(clean_rows) != len(source_rows):
        raise ValueError("Clean row count changed unexpectedly")
    if set(row["ERA"] for row in clean_rows) != {"2000-2004", "2005-2021", "2022-2026"}:
        raise ValueError("ERA categories are incomplete")
    if any(row["PRIMARY_POS"] == "" for row in clean_rows):
        raise ValueError("A Clean row has no PRIMARY_POS")
    bar_values = [float(row["BAR_NUM"]) for row in clean_rows if row["BAR_NUM"] != "NA"]
    if not all(0.97 <= value <= 1.18 for value in bar_values):
        raise ValueError("A Clean BAR value falls outside 0.97 to 1.18")
    if len(invalid_rows) != 2 or not danny_granger_seen:
        raise ValueError("Expected all three named records were not found")

    # Put each ERA in one block, then sort within the block by PRIMARY_POS.
    # YEAR and PLAYER make the result deterministic without changing the requested grouping.
    clean_rows.sort(
        key=lambda row: (
            ERA_ORDER[row["ERA"]],
            row["PRIMARY_POS"],
            int(row["YEAR"]),
            row["PLAYER"],
        )
    )
    row_numbers = {
        (row["PLAYER"], int(row["YEAR"])): index
        for index, row in enumerate(clean_rows, start=2)
    }
    dunn_excel_row = row_numbers[("Dunn, Kris", 2016)]
    beasley_excel_row = row_numbers[("Beasley, Malik", 2016)]
    danny_granger_row = row_numbers[("Granger, Danny", 2005)]

    era_ranges: dict[str, tuple[int, int]] = {}
    position_ranges: dict[tuple[str, str], tuple[int, int]] = {}
    for excel_row, row in enumerate(clean_rows, start=2):
        era_ranges.setdefault(row["ERA"], (excel_row, excel_row))
        era_ranges[row["ERA"]] = (era_ranges[row["ERA"]][0], excel_row)
        position_key = (row["ERA"], row["PRIMARY_POS"])
        position_ranges.setdefault(position_key, (excel_row, excel_row))
        position_ranges[position_key] = (position_ranges[position_key][0], excel_row)

    log_headers = ["What", "Where", "Rows Before", "Rows After", "Rows Removed", "Because", "Decided By"]
    n_rows = len(source_rows)
    dunn_excel_row = invalid_rows["dunn"]
    beasley_excel_row = invalid_rows["beasley"]
    log_rows = [
        rows_for_log(
            n_rows,
            "Zero weight is not a real measurement; the data dictionary requires it to remain missing.",
            f"Clean!E{dunn_excel_row}; Raw!E{dunn_excel_row}; Dunn, Kris, 2016",
            "Set Kris Dunn's 2016 WGT from 0.0 to NA",
            "me",
        ),
        rows_for_log(
            n_rows,
            "BMI derived from the invalid zero weight is not valid, so it remains missing with the weight.",
            f"Clean!F{dunn_excel_row}; Raw!F{dunn_excel_row}; Dunn, Kris, 2016",
            "Set Kris Dunn's 2016 BMI from 0.0 to NA",
            "me",
        ),
        rows_for_log(
            n_rows,
            "A zero shuttle result is not a real recorded time; keep it missing rather than treating it as fastest.",
            f"Clean!O{beasley_excel_row}; Raw!O{beasley_excel_row}; Beasley, Malik, 2016",
            "Set Malik Beasley's 2016 SHUTTLE from 0.00 to NA",
            "me",
        ),
        rows_for_log(
            n_rows,
            "Bench zeros are real results and must remain distinguishable from NA.",
            "Clean!Q2:Q1750; 39 source zeros retained",
            "Retain all 39 bench-press zeros",
            "me",
        ),
        rows_for_log(
            n_rows,
            "Both 4.00-second sprint values are valid recorded results and are not missing values.",
            "Clean!P2:P1750; two source values equal to 4.00 retained",
            "Retain both 4.00-second sprints",
            "me",
        ),
        rows_for_log(
            n_rows,
            "The user explicitly requested that sparse shuttle, bench, body-fat, hand-length, and hand-width fields remain in Clean, with NA preserved.",
            "Clean!G2:G1750, J2:K1750, O2:O1750, Q2:Q1750",
            "Keep shuttle, bench press, body fat, and hand measures",
            "me",
        ),
        rows_for_log(
            n_rows,
            "BAR is stored in Raw as percent text; convert it to a ratio so it can be calculated and checked against 0.97–1.18.",
            "Clean!R2:R1750; Raw!R2:R1750 remains unchanged text",
            "Convert BAR from percent text to a numeric ratio",
            "me",
        ),
        rows_for_log(
            n_rows,
            "BAR_NUM was not separately defined; I made it an explicit numeric audit copy of normalized Clean!BAR while Raw!BAR preserves the source text.",
            "Clean!V2:V1750",
            "Add BAR_NUM as a numeric helper equal to normalized BAR",
            "agent",
        ),
        rows_for_log(
            n_rows,
            "The user requested that Clean!BAR match the original Raw text; BAR_NUM remains the only numeric BAR field.",
            "Clean!R2:R1750 restored from Raw!R2:R1750; Clean!V2:V1750 remains numeric",
            "Restore Clean BAR to the original Raw text",
            "me",
        ),
        rows_for_log(
            n_rows,
            "Use the first POS code; for the requested 2005 Danny Granger record, POS is NA, so PRIMARY_POS is 'none recorded'.",
            f"Clean!W2:W1750; Danny Granger at Clean!W{danny_granger_row}",
            "Add PRIMARY_POS",
            "me",
        ),
        rows_for_log(
            n_rows,
            "Assign 2000–2004, 2022–2026, and 2005–2021 to every Clean row using YEAR.",
            "Clean!X2:X1750",
            "Add ERA",
            "me",
        ),
        rows_for_log(
            n_rows,
            "The user requested one contiguous block for each ERA and PRIMARY_POS group so the benchmark ranges are auditable.",
            "Clean!A2:X1750",
            "Sort Clean by ERA, then PRIMARY_POS",
            "me",
        ),
        rows_for_log(
            n_rows,
            "No rows were dropped; Clean has the same 1,749 data rows as Raw after the requested cell-level corrections.",
            "Clean!A2:X1750 compared with Raw!A2:U1750",
            "Retain all prospect rows",
            "me",
        ),
        rows_for_log(
            n_rows,
            "Required attribution: Kaggle dataset NBA Draft Combine, CC BY 4.0, https://www.kaggle.com/datasets/marcusfern/nba-draft-combine",
            "Decision_Log source record",
            "Record source attribution",
            "agent, approved",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="qian_lab4_build_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        clean_csv = temp_dir / "clean.csv"
        log_csv = temp_dir / "decision_log.csv"

        with clean_csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=clean_headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows(clean_rows)

        with log_csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow(log_headers)
            writer.writerows(log_rows)

        run("create", str(OUTPUT_XLSX), "--type", "xlsx", "--force", "--locale", "en-US")
        run("set", str(OUTPUT_XLSX), "/Sheet1", "--prop", "name=Raw")
        run("add", str(OUTPUT_XLSX), "/", "--type", "sheet", "--prop", "name=Clean")
        run("add", str(OUTPUT_XLSX), "/", "--type", "sheet", "--prop", "name=Decision_Log")
        run("add", str(OUTPUT_XLSX), "/", "--type", "sheet", "--prop", "name=Benchmarks")

        # Raw is imported directly from the unchanged source CSV.
        run("import", str(OUTPUT_XLSX), "/Raw", "--file", str(SOURCE_CSV), "--header")
        run("import", str(OUTPUT_XLSX), "/Clean", "--file", str(clean_csv), "--header")
        run("import", str(OUTPUT_XLSX), "/Decision_Log", "--file", str(log_csv), "--header")

    # Tables provide filters and readable banding without changing cell values.
    run("add", str(OUTPUT_XLSX), "/Raw", "--type", "table", "--prop", "ref=A1:U1750", "--prop", "name=RawData", "--prop", "displayName=RawData", "--prop", "style=medium2")
    run("add", str(OUTPUT_XLSX), "/Clean", "--type", "table", "--prop", "ref=A1:X1750", "--prop", "name=CleanData", "--prop", "displayName=CleanData", "--prop", "style=medium2")
    run("add", str(OUTPUT_XLSX), "/Decision_Log", "--type", "table", "--prop", f"ref=A1:G{len(log_rows) + 1}", "--prop", "name=DecisionLog", "--prop", "displayName=DecisionLog", "--prop", "style=light2")

    # Build a formula-driven benchmark summary. Every statistic reads its values
    # directly from the sorted Clean blocks, so the workbook remains auditable.
    benchmark_operations: list[dict] = []

    summary_headers = [
        "Measure", "Clean column", "Center to read",
        "2000-2004 Count", "2000-2004 Mean", "2000-2004 Median",
        "2000-2004 P25", "2000-2004 P75",
        "2022-2026 Count", "2022-2026 Mean", "2022-2026 Median",
        "2022-2026 P25", "2022-2026 P75",
    ]
    for column_index, value in enumerate(summary_headers):
        benchmark_operations.append({
            "command": "set",
            "path": f"/Benchmarks/{chr(ord('A') + column_index)}1",
            "props": {"value": value},
        })

    for row_number, (label, column, _field, center) in enumerate(MEASURE_SPECS, start=2):
        for column_letter, value in zip(("A", "B", "C"), (label, column, center)):
            benchmark_operations.append({
                "command": "set",
                "path": f"/Benchmarks/{column_letter}{row_number}",
                "props": {"value": value},
            })
        for era, start_column in zip(TARGET_ERAS, ("D", "I")):
            first_row, last_row = era_ranges[era]
            clean_range = f"Clean!${column}${first_row}:${column}${last_row}"
            formulas = (
                f"COUNT({clean_range})",
                f"AVERAGE({clean_range})",
                f"MEDIAN({clean_range})",
                f"PERCENTILE.INC({clean_range},0.25)",
                f"PERCENTILE.INC({clean_range},0.75)",
            )
            for offset, formula in enumerate(formulas):
                benchmark_operations.append({
                    "command": "set",
                    "path": f"/Benchmarks/{chr(ord(start_column) + offset)}{row_number}",
                    "props": {"formula": formula},
                })

    benchmark_operations.extend([
        {
            "command": "set",
            "path": "/Benchmarks/A10",
            "props": {"value": "All statistics are formulas referencing numeric values in Clean; text NA is excluded."},
        },
        {"command": "set", "path": "/Benchmarks/A12", "props": {"value": "PRIMARY_POS"}},
        {"command": "set", "path": "/Benchmarks/B12", "props": {"value": "2000-2004 max LPVERT"}},
        {"command": "set", "path": "/Benchmarks/C12", "props": {"value": "2022-2026 max LPVERT"}},
    ])

    positions = sorted({
        row["PRIMARY_POS"]
        for row in clean_rows
        if row["ERA"] in TARGET_ERAS
    })
    for row_number, primary_pos in enumerate(positions, start=13):
        benchmark_operations.append({
            "command": "set",
            "path": f"/Benchmarks/A{row_number}",
            "props": {"value": primary_pos},
        })
        for column_letter, era in zip(("B", "C"), TARGET_ERAS):
            first_row, last_row = position_ranges[(era, primary_pos)]
            clean_range = f"Clean!$M${first_row}:$M${last_row}"
            formula = f'IF(COUNT({clean_range})=0,"",MAX({clean_range}))'
            benchmark_operations.append({
                "command": "set",
                "path": f"/Benchmarks/{column_letter}{row_number}",
                "props": {"formula": formula},
            })

    run_batch(benchmark_operations)
    run("add", str(OUTPUT_XLSX), "/Benchmarks", "--type", "table", "--prop", "ref=A1:M8", "--prop", "name=BenchmarkSummary", "--prop", "displayName=BenchmarkSummary", "--prop", "style=medium2")
    run("add", str(OUTPUT_XLSX), "/Benchmarks", "--type", "table", "--prop", f"ref=A12:C{12 + len(positions)}", "--prop", "name=MaxVerticalByPosition", "--prop", "displayName=MaxVerticalByPosition", "--prop", "style=light2")

    # Formatting and print setup. Values remain unchanged by these commands.
    widths = {
        "Raw": {"A": 10, "B": 24, "C": 10, "D": 10, "E": 10, "F": 10, "G": 10, "H": 12, "I": 12, "J": 10, "K": 10, "L": 12, "M": 12, "N": 10, "O": 10, "P": 10, "Q": 10, "R": 10, "S": 10, "T": 12, "U": 12},
        "Clean": {"A": 10, "B": 24, "C": 12, "D": 10, "E": 10, "F": 10, "G": 10, "H": 12, "I": 12, "J": 10, "K": 10, "L": 12, "M": 12, "N": 10, "O": 10, "P": 10, "Q": 10, "R": 10, "S": 10, "T": 12, "U": 12, "V": 12, "W": 16, "X": 12},
        "Decision_Log": {"A": 42, "B": 48, "C": 14, "D": 14, "E": 14, "F": 72, "G": 14},
        "Benchmarks": {"A": 24, "B": 14, "C": 16, "D": 16, "E": 16, "F": 16, "G": 16, "H": 16, "I": 16, "J": 16, "K": 16, "L": 16, "M": 16},
    }
    for sheet, columns in widths.items():
        run("set", str(OUTPUT_XLSX), f"/{sheet}", "--prop", "freeze=A2", "--prop", "orientation=landscape", "--prop", "fitToPage=1x0", "--prop", "printTitleRows=1:1")
        for column, width in columns.items():
            run("set", str(OUTPUT_XLSX), f"/{sheet}/col[{column}]", "--prop", f"width={width}")
        last_column = max(columns)
        run("set", str(OUTPUT_XLSX), f"/{sheet}/A1:{last_column}1", "--prop", "font.bold=true", "--prop", "fill=1F4E78", "--prop", "font.color=FFFFFF", "--prop", "alignment.horizontal=center", "--prop", "alignment.wrapText=true")

    # Number formats for the normalized BAR fields and the integer year.
    for sheet in ("Raw", "Clean"):
        run("set", str(OUTPUT_XLSX), f"/{sheet}/A2:A1750", "--prop", "numberformat=0")
    run("set", str(OUTPUT_XLSX), "/Clean/R2:R1750", "--prop", "numberformat=0.000")
    run("set", str(OUTPUT_XLSX), "/Clean/V2:V1750", "--prop", "numberformat=0.000")
    run("set", str(OUTPUT_XLSX), "/Benchmarks/D2:D8", "--prop", "numberformat=0")
    run("set", str(OUTPUT_XLSX), "/Benchmarks/I2:I8", "--prop", "numberformat=0")
    run("set", str(OUTPUT_XLSX), "/Benchmarks/E2:H8", "--prop", "numberformat=0.00")
    run("set", str(OUTPUT_XLSX), "/Benchmarks/J2:M8", "--prop", "numberformat=0.00")
    run("set", str(OUTPUT_XLSX), f"/Benchmarks/B13:C{12 + len(positions)}", "--prop", "numberformat=0.00")

    run("validate", str(OUTPUT_XLSX))
    print(f"Built {OUTPUT_XLSX} with {len(source_rows)} Raw rows, {len(clean_rows)} Clean rows, and {len(log_rows)} Decision_Log entries.")


if __name__ == "__main__":
    main()
