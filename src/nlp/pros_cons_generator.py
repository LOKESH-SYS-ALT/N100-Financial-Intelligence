from pathlib import Path
import sqlite3
import re
import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_PATH = PROJECT_ROOT / "output" / "pros_cons_generated.csv"


# ============================================================
# DATABASE
# ============================================================


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_companies():
    conn = get_connection()

    query = """
        SELECT
            id AS company_id,
            company_name,
            roce_percentage,
            roe_percentage
        FROM companies
        ORDER BY id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def load_ratios():
    conn = get_connection()

    query = """
        SELECT *
        FROM financial_ratios
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# ============================================================
# HELPERS
# ============================================================


def numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def latest_row(group):
    group = group.copy()

    def year_number(value):
        if pd.isna(value):
            return -1

        text = str(value).strip()

        if text.upper() == "TTM":
            return 9999

        match = re.search(r"(\d{4})", text)

        if match:
            return int(match.group(1))

        return -1

    group["_year_number"] = group["year"].apply(year_number)

    group = group.sort_values(
        "_year_number",
        ascending=True,
        na_position="last",
    )

    return group.iloc[-1]


def confidence_from_strength(strength):
    strength = max(0.0, min(1.0, strength))
    return round(61 + strength * 39, 2)


def add_signal(signals, company_id, signal_type, rule_id, text, confidence):
    signals.append(
        {
            "company_id": company_id,
            "type": signal_type,
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": round(float(confidence), 2),
        }
    )


# ============================================================
# PRO RULES
# ============================================================


def generate_pros(group, company_id, signals):

    group = group.copy()

    latest = latest_row(group)

    # --------------------------------------------------------
    # PRO_01 — Sustained ROE > 20%
    # --------------------------------------------------------

    if "return_on_equity_pct" in group.columns:

        roe = pd.to_numeric(
            group["return_on_equity_pct"],
            errors="coerce",
        ).dropna()

        if len(roe) >= 3 and (roe.tail(3) > 20).all():

            strength = min(
                1,
                (roe.tail(3).mean() - 20) / 30,
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_01",
                "ROE has remained above 20% across the latest three available periods, indicating strong shareholder returns.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_02 — Positive FCF for 5 consecutive periods
    # --------------------------------------------------------

    if "free_cash_flow_cr" in group.columns:

        fcf = pd.to_numeric(
            group["free_cash_flow_cr"],
            errors="coerce",
        ).dropna()

        if len(fcf) >= 5 and (fcf.tail(5) > 0).all():

            strength = min(
                1,
                fcf.tail(5).mean() / max(abs(fcf.tail(5).mean()), 1),
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_02",
                "Free cash flow has remained positive across the latest five available periods.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_03 — Debt free latest period
    # --------------------------------------------------------

    if "debt_to_equity" in group.columns:

        de = numeric(latest.get("debt_to_equity"))

        if de is not None and de == 0:

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_03",
                "The latest available debt-to-equity ratio is zero, indicating a debt-free balance sheet.",
                95,
            )

    # --------------------------------------------------------
    # PRO_04 — Revenue CAGR > 15%
    # --------------------------------------------------------

    if "revenue_cagr_5yr" in group.columns:

        value = numeric(latest.get("revenue_cagr_5yr"))

        if value is not None and value > 15:

            strength = min(
                1,
                (value - 15) / 25,
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_04",
                f"Five-year revenue CAGR is {value:.2f}%, above the 15% growth threshold.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_05 — Operating margin > 25%
    # --------------------------------------------------------

    if "operating_profit_margin_pct" in group.columns:

        value = numeric(latest.get("operating_profit_margin_pct"))

        if value is not None and value > 25:

            strength = min(
                1,
                (value - 25) / 25,
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_05",
                f"Latest operating profit margin is {value:.2f}%, indicating strong operating profitability.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_06 — PAT CAGR > 20%
    # --------------------------------------------------------

    if "pat_cagr_5yr" in group.columns:

        value = numeric(latest.get("pat_cagr_5yr"))

        if value is not None and value > 20:

            strength = min(
                1,
                (value - 20) / 30,
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_06",
                f"Five-year PAT CAGR is {value:.2f}%, showing strong profit growth.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_07 — Strong interest coverage / debt free
    # --------------------------------------------------------

    icr = numeric(latest.get("interest_coverage"))
    de = numeric(latest.get("debt_to_equity"))

    if (icr is not None and icr > 10) or (de is not None and de == 0):

        if icr is not None and icr > 10:

            strength = min(
                1,
                (icr - 10) / 20,
            )

            text = (
                f"Latest interest coverage is {icr:.2f}x, "
                "providing a strong buffer for interest obligations."
            )

        else:

            strength = 0.9

            text = (
                "The latest debt-to-equity ratio is zero, "
                "eliminating conventional interest-bearing leverage risk."
            )

        add_signal(
            signals,
            company_id,
            "pro",
            "PRO_07",
            text,
            confidence_from_strength(strength),
        )

    # --------------------------------------------------------
    # PRO_08 — EPS CAGR > 15%
    # --------------------------------------------------------

    if "eps_cagr_5yr" in group.columns:

        value = numeric(latest.get("eps_cagr_5yr"))

        if value is not None and value > 15:

            strength = min(
                1,
                (value - 15) / 25,
            )

            add_signal(
                signals,
                company_id,
                "pro",
                "PRO_08",
                f"Five-year EPS CAGR is {value:.2f}%, indicating strong per-share earnings growth.",
                confidence_from_strength(strength),
            )

    # --------------------------------------------------------
    # PRO_09 — Improving ROE over 3 consecutive periods
    # --------------------------------------------------------

    if "return_on_equity_pct" in group.columns:

        roe = pd.to_numeric(
            group["return_on_equity_pct"],
            errors="coerce",
        ).dropna()

        if len(roe) >= 3:

            last3 = roe.tail(3)

            if last3.iloc[1] > last3.iloc[0] and last3.iloc[2] > last3.iloc[1]:

                add_signal(
                    signals,
                    company_id,
                    "pro",
                    "PRO_09",
                    "ROE has improved in each of the latest three available periods.",
                    90,
                )

    # --------------------------------------------------------
    # PRO_10 — PAT CAGR > Revenue CAGR
    # --------------------------------------------------------

    revenue = numeric(latest.get("revenue_cagr_5yr"))
    pat = numeric(latest.get("pat_cagr_5yr"))

    if revenue is not None and pat is not None and pat > revenue:

        strength = min(
            1,
            (pat - revenue) / 20,
        )

        add_signal(
            signals,
            company_id,
            "pro",
            "PRO_10",
            f"PAT CAGR of {pat:.2f}% exceeds revenue CAGR of {revenue:.2f}%, suggesting profit growth is outpacing sales growth.",
            confidence_from_strength(strength),
        )

    # --------------------------------------------------------
    # PRO_11 — Improving ROCE
    # --------------------------------------------------------

    if "return_on_capital_employed_pct" in group.columns:

        roce = pd.to_numeric(
            group["return_on_capital_employed_pct"],
            errors="coerce",
        ).dropna()

        if len(roce) >= 3:

            last3 = roce.tail(3)

            if last3.iloc[1] > last3.iloc[0] and last3.iloc[2] > last3.iloc[1]:

                add_signal(
                    signals,
                    company_id,
                    "pro",
                    "PRO_11",
                    "ROCE has improved across the latest three available periods.",
                    88,
                )

    # --------------------------------------------------------
    # PRO_12 — Strong ROCE latest
    # --------------------------------------------------------

    roce = numeric(latest.get("return_on_capital_employed_pct"))

    if roce is not None and roce > 20:

        strength = min(
            1,
            (roce - 20) / 30,
        )

        add_signal(
            signals,
            company_id,
            "pro",
            "PRO_12",
            f"Latest ROCE is {roce:.2f}%, indicating strong capital efficiency.",
            confidence_from_strength(strength),
        )


# ============================================================
# CON RULES
# ============================================================


def generate_cons(group, company_id, signals):

    group = group.copy()

    latest = latest_row(group)

    # --------------------------------------------------------
    # CON_01 — D/E > 2
    # --------------------------------------------------------

    de = numeric(latest.get("debt_to_equity"))

    if de is not None and de > 2:

        strength = min(
            1,
            (de - 2) / 4,
        )

        add_signal(
            signals,
            company_id,
            "con",
            "CON_01",
            f"Latest debt-to-equity is {de:.2f}x, indicating elevated balance-sheet leverage.",
            confidence_from_strength(strength),
        )

    # --------------------------------------------------------
    # CON_02 — Negative FCF for 3 consecutive periods
    # --------------------------------------------------------

    if "free_cash_flow_cr" in group.columns:

        fcf = pd.to_numeric(
            group["free_cash_flow_cr"],
            errors="coerce",
        ).dropna()

        if len(fcf) >= 3 and (fcf.tail(3) < 0).all():

            add_signal(
                signals,
                company_id,
                "con",
                "CON_02",
                "Free cash flow has remained negative across the latest three available periods.",
                90,
            )

    # --------------------------------------------------------
    # CON_03 — Operating margin declining 3 periods
    # --------------------------------------------------------

    if "operating_profit_margin_pct" in group.columns:

        opm = pd.to_numeric(
            group["operating_profit_margin_pct"],
            errors="coerce",
        ).dropna()

        if len(opm) >= 3:

            last3 = opm.tail(3)

            if last3.iloc[1] < last3.iloc[0] and last3.iloc[2] < last3.iloc[1]:

                add_signal(
                    signals,
                    company_id,
                    "con",
                    "CON_03",
                    "Operating profit margin has declined across the latest three available periods.",
                    90,
                )

    # --------------------------------------------------------
    # CON_04 — Negative profit margin latest
    # --------------------------------------------------------

    npm = numeric(latest.get("net_profit_margin_pct"))

    if npm is not None and npm < 0:

        add_signal(
            signals,
            company_id,
            "con",
            "CON_04",
            f"Latest net profit margin is negative at {npm:.2f}%.",
            95,
        )

    # --------------------------------------------------------
    # CON_05 — ICR < 1.5
    # --------------------------------------------------------

    icr = numeric(latest.get("interest_coverage"))

    if icr is not None and icr < 1.5:

        add_signal(
            signals,
            company_id,
            "con",
            "CON_05",
            f"Latest interest coverage is only {icr:.2f}x, indicating limited interest-payment protection.",
            95,
        )

    # --------------------------------------------------------
    # CON_06 — Payout > 100%
    # --------------------------------------------------------

    payout = numeric(latest.get("dividend_payout_ratio_pct"))

    if payout is not None and payout > 100:

        strength = min(
            1,
            (payout - 100) / 100,
        )

        add_signal(
            signals,
            company_id,
            "con",
            "CON_06",
            f"Latest dividend payout ratio is {payout:.2f}%, above 100% of reported earnings.",
            confidence_from_strength(strength),
        )

    # --------------------------------------------------------
    # CON_07 — D/E rising 3 consecutive periods
    # --------------------------------------------------------

    if "debt_to_equity" in group.columns:

        de_series = pd.to_numeric(
            group["debt_to_equity"],
            errors="coerce",
        ).dropna()

        if len(de_series) >= 3:

            last3 = de_series.tail(3)

            if last3.iloc[1] > last3.iloc[0] and last3.iloc[2] > last3.iloc[1]:

                add_signal(
                    signals,
                    company_id,
                    "con",
                    "CON_07",
                    "Debt-to-equity has increased across the latest three available periods.",
                    90,
                )

    # --------------------------------------------------------
    # CON_08 — EPS declining 3 consecutive periods
    # --------------------------------------------------------

    if "earnings_per_share" in group.columns:

        eps = pd.to_numeric(
            group["earnings_per_share"],
            errors="coerce",
        ).dropna()

        if len(eps) >= 3:

            last3 = eps.tail(3)

            if last3.iloc[1] < last3.iloc[0] and last3.iloc[2] < last3.iloc[1]:

                add_signal(
                    signals,
                    company_id,
                    "con",
                    "CON_08",
                    "EPS has declined across the latest three available periods.",
                    90,
                )

    # --------------------------------------------------------
    # CON_09 — ROCE < 10%
    # --------------------------------------------------------

    roce = numeric(latest.get("return_on_capital_employed_pct"))

    if roce is not None and roce < 10:

        strength = min(
            1,
            (10 - roce) / 10,
        )

        add_signal(
            signals,
            company_id,
            "con",
            "CON_09",
            f"Latest ROCE is only {roce:.2f}%, indicating weak capital efficiency.",
            confidence_from_strength(strength),
        )

    # --------------------------------------------------------
    # CON_10 — High leverage flag
    # --------------------------------------------------------

    high_leverage = numeric(latest.get("high_leverage_flag"))

    if high_leverage == 1:

        add_signal(
            signals,
            company_id,
            "con",
            "CON_10",
            "The latest financial-ratio record is flagged for high leverage.",
            90,
        )

    # --------------------------------------------------------
    # CON_11 — Weak revenue CAGR
    # --------------------------------------------------------

    revenue = numeric(latest.get("revenue_cagr_5yr"))

    if revenue is not None and revenue < 5:

        add_signal(
            signals,
            company_id,
            "con",
            "CON_11",
            f"Five-year revenue CAGR is only {revenue:.2f}%, below the 5% growth threshold.",
            90,
        )

    # --------------------------------------------------------
    # CON_12 — Weak PAT / EPS growth
    # --------------------------------------------------------

    pat = numeric(latest.get("pat_cagr_5yr"))

    eps_cagr = numeric(latest.get("eps_cagr_5yr"))

    weak_metrics = []

    if pat is not None and pat < 5:
        weak_metrics.append(f"PAT CAGR {pat:.2f}%")

    if eps_cagr is not None and eps_cagr < 5:
        weak_metrics.append(f"EPS CAGR {eps_cagr:.2f}%")

    if weak_metrics:

        add_signal(
            signals,
            company_id,
            "con",
            "CON_12",
            "Weak earnings growth: " + ", ".join(weak_metrics) + ".",
            88,
        )


# ============================================================
# FALLBACK SIGNALS
# ============================================================


def add_fallback_signals(group, company_id, signals):

    company_signals = [x for x in signals if x["company_id"] == company_id]

    has_pro = any(x["type"] == "pro" for x in company_signals)

    has_con = any(x["type"] == "con" for x in company_signals)

    latest = latest_row(group)

    # --------------------------------------------------------
    # PRO FALLBACK
    # --------------------------------------------------------

    if not has_pro:

        roe = numeric(latest.get("return_on_equity_pct"))

        roce = numeric(latest.get("return_on_capital_employed_pct"))

        fcf = numeric(latest.get("free_cash_flow_cr"))

        if roe is not None:

            text = (
                f"Baseline positive signal: latest ROE is "
                f"{roe:.2f}%; no higher-threshold Pro rule was triggered."
            )

        elif roce is not None:

            text = (
                f"Baseline positive signal: latest ROCE is "
                f"{roce:.2f}%; no higher-threshold Pro rule was triggered."
            )

        elif fcf is not None and fcf > 0:

            text = (
                f"Baseline positive signal: latest free cash flow is "
                f"{fcf:.2f} Cr; no higher-threshold Pro rule was triggered."
            )

        else:

            text = (
                "Baseline positive signal: financial data is available "
                "for review, but no higher-threshold Pro rule was triggered."
            )

        add_signal(
            signals,
            company_id,
            "pro",
            "PRO_FALLBACK",
            text,
            61,
        )

    # --------------------------------------------------------
    # CON FALLBACK
    # --------------------------------------------------------

    if not has_con:

        de = numeric(latest.get("debt_to_equity"))

        revenue = numeric(latest.get("revenue_cagr_5yr"))

        pat = numeric(latest.get("pat_cagr_5yr"))

        if de is not None:

            text = (
                f"Baseline review signal: latest debt-to-equity is "
                f"{de:.2f}x; no higher-threshold Con rule was triggered."
            )

        elif revenue is not None:

            text = (
                f"Baseline review signal: latest available five-year "
                f"revenue CAGR is {revenue:.2f}%; no higher-threshold "
                "Con rule was triggered."
            )

        elif pat is not None:

            text = (
                f"Baseline review signal: latest available five-year "
                f"PAT CAGR is {pat:.2f}%; no higher-threshold "
                "Con rule was triggered."
            )

        else:

            text = (
                "Baseline review signal: financial data is available "
                "for review, but no higher-threshold Con rule was triggered."
            )

        add_signal(
            signals,
            company_id,
            "con",
            "CON_FALLBACK",
            text,
            61,
        )


# ============================================================
# MAIN GENERATOR
# ============================================================


def generate_pros_cons():

    companies = load_companies()
    ratios = load_ratios()

    signals = []

    if ratios.empty:

        raise RuntimeError("financial_ratios table is empty.")

    for company_id in companies["company_id"]:

        group = ratios[ratios["company_id"].astype(str) == str(company_id)].copy()

        if group.empty:
            continue

        generate_pros(
            group,
            company_id,
            signals,
        )

        generate_cons(
            group,
            company_id,
            signals,
        )

        add_fallback_signals(
            group,
            company_id,
            signals,
        )

    output = pd.DataFrame(signals)

    if output.empty:

        raise RuntimeError("No Pros/Cons signals were generated.")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = output[
        [
            "company_id",
            "type",
            "rule_id",
            "text",
            "confidence_pct",
        ]
    ]

    output.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return output, companies


# ============================================================
# VERIFICATION
# ============================================================


def verify_output(output, companies):

    company_ids = set(companies["company_id"].astype(str))

    output_company_ids = set(output["company_id"].astype(str))

    missing_companies = sorted(company_ids - output_company_ids)

    pro_companies = set(
        output.loc[
            output["type"] == "pro",
            "company_id",
        ].astype(str)
    )

    con_companies = set(
        output.loc[
            output["type"] == "con",
            "company_id",
        ].astype(str)
    )

    missing_pro = sorted(company_ids - pro_companies)

    missing_con = sorted(company_ids - con_companies)

    print()
    print("=" * 60)
    print("PROS / CONS VERIFICATION")
    print("=" * 60)

    print(f"Companies in companies table : {len(company_ids)}")

    print(f"Companies with output         : {len(output_company_ids)}")

    print(f"Total generated signals       : {len(output)}")

    print(f"Pro signals                   : " f"{(output['type'] == 'pro').sum()}")

    print(f"Con signals                   : " f"{(output['type'] == 'con').sum()}")

    print(f"Companies missing any output  : " f"{len(missing_companies)}")

    print(f"Companies missing Pro         : " f"{len(missing_pro)}")

    print(f"Companies missing Con         : " f"{len(missing_con)}")

    if missing_companies:

        print()
        print("Missing companies:")
        print(missing_companies)

    if missing_pro:

        print()
        print("Missing Pro:")
        print(missing_pro)

    if missing_con:

        print()
        print("Missing Con:")
        print(missing_con)

    print()

    if not missing_companies and not missing_pro and not missing_con:

        print("SUCCESS: All 92 companies have at least " "one Pro and one Con signal.")

    else:

        print("REVIEW REQUIRED: Some companies do not have " "both Pro and Con.")

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    output, companies = generate_pros_cons()

    print(f"Generated file: {OUTPUT_PATH}")

    print(f"Generated rows: {len(output)}")

    verify_output(
        output,
        companies,
    )
