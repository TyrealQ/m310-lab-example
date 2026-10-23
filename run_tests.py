from math import isfinite, sqrt
from pathlib import Path
from statistics import mean, stdev

from openpyxl import load_workbook
from scipy.stats import linregress, pearsonr, ttest_ind


WORKBOOK = Path(__file__).with_name("QIAN_LAB4.xlsx")

GROUP_YEARS = {
    "2000-2004": set(range(2000, 2005)),
    "2022-2026": set(range(2022, 2027)),
}


def main():
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    sheet = workbook["Clean"]

    headers = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
    column = {name: index for index, name in enumerate(headers)}
    values = {group: [] for group in GROUP_YEARS}
    era_mismatches = []
    rows = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        year = row[column["YEAR"]]
        era = row[column["ERA"]]
        hgt = row[column["HGT"]]
        lpvert = row[column["LPVERT"]]
        rows.append((year, era, hgt, lpvert))

        for group, years in GROUP_YEARS.items():
            if year in years:
                if era != group:
                    era_mismatches.append((year, era, group))
                if isinstance(lpvert, (int, float)) and isfinite(lpvert):
                    values[group].append(float(lpvert))
                break

    if era_mismatches:
        raise ValueError(f"YEAR/ERA mismatches found: {era_mismatches[:5]}")

    early = values["2000-2004"]
    recent = values["2022-2026"]
    difference = mean(recent) - mean(early)

    # Welch's independent-samples t-test; recent group is first for direction.
    t_result = ttest_ind(recent, early, equal_var=False, alternative="two-sided")

    # Cohen's d, using the pooled sample standard deviation.
    pooled_sd = sqrt(
        ((len(recent) - 1) * stdev(recent) ** 2
         + (len(early) - 1) * stdev(early) ** 2)
        / (len(recent) + len(early) - 2)
    )
    cohen_d = difference / pooled_sd

    correlation_pairs = [
        (hgt, lpvert)
        for year, _, hgt, lpvert in rows
        if year in GROUP_YEARS["2022-2026"]
        and isinstance(hgt, (int, float))
        and isfinite(hgt)
        and isinstance(lpvert, (int, float))
        and isfinite(lpvert)
    ]
    correlation_hgt, correlation_lpvert = zip(*correlation_pairs)
    correlation = pearsonr(correlation_hgt, correlation_lpvert)

    regression_pairs = [
        (year, lpvert)
        for year, _, _, lpvert in rows
        if isinstance(year, (int, float))
        and isfinite(year)
        and isinstance(lpvert, (int, float))
        and isfinite(lpvert)
    ]
    regression_years, regression_lpverts = zip(*regression_pairs)
    regression = linregress(regression_years, regression_lpverts)

    print(f"2000-2004: n={len(early)}, mean_LPVERT={mean(early):.2f} inches")
    print(f"2022-2026: n={len(recent)}, mean_LPVERT={mean(recent):.2f} inches")
    print(f"difference (2022-2026 - 2000-2004)={difference:.2f} inches")
    print(f"Welch t statistic={t_result.statistic:.6f}")
    print(f"two-sided p-value={t_result.pvalue:.6g}")
    print(f"Cohen's d={cohen_d:.6f}")
    print(
        f"2022-2026 HGT-LPVERT correlation: n={len(correlation_pairs)}, "
        f"r={correlation.statistic:.6f}, p-value={correlation.pvalue:.6g}"
    )
    print(
        f"all-years LPVERT on YEAR regression: n={len(regression_pairs)}, "
        f"slope={regression.slope:.6f} inches/year, "
        f"p-value={regression.pvalue:.6g}"
    )


if __name__ == "__main__":
    main()
