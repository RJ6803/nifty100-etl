from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

DATABASE_PATH = "data/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pros_cons_generated.csv"


# ==========================================================
# DATABASE
# ==========================================================

class ProsConsGenerator:

    def __init__(self, database_path=DATABASE_PATH):

        self.database_path = database_path

        if not Path(database_path).exists():
            raise FileNotFoundError(
                f"Database not found: {database_path}"
            )

        self.conn = sqlite3.connect(database_path)

        self.load_data()

    # ------------------------------------------------------

    def load_data(self):
        self.ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        self.cashflow = pd.read_sql(
            "SELECT * FROM cashflow_intelligence",
            self.conn
        )
        print("\nCashflow Intelligence Columns")
        print(self.cashflow.columns.tolist())

        self.companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )
        if "company_id" not in self.companies.columns:
            self.companies.rename(
                columns={"id": "company_id"},
                inplace=True
            )

        print("\nRatios Columns")
        print(self.ratios.columns.tolist())

        print("\nCashflow Columns")
        print(self.cashflow.columns.tolist())

        print("\nCompany Columns")
        print(self.companies.columns.tolist())

        # Merge company information
        self.companies=self.companies.drop_duplicates("company_id")
        self.ratios = self.ratios.merge(

            self.companies,

            on="company_id",

            how="left"

        )

        # Sort oldest -> newest

        if "year_num" in self.ratios.columns:

            self.ratios = self.ratios.sort_values(

                ["company_id", "year_num"]

            )

        else:

            self.ratios = self.ratios.sort_values(

                ["company_id", "year"]

            )

    # ======================================================
    # COMPANY HISTORY
    # ======================================================

    def company_history(self, company_id):

        """
        Return complete historical ratios
        for one company.
        """

        df = self.ratios[
            self.ratios.company_id == company_id
        ].copy()

        return df.reset_index(drop=True)

    # ------------------------------------------------------

    def latest_row(self, company_id):

        history = self.company_history(company_id)

        if history.empty:
            return None

        return history.iloc[-1]

    # ======================================================
    # SAFE VALUE
    # ======================================================

    @staticmethod
    def safe_number(value, default=0):
        if value is None:
            return default

        try:

            if pd.isna(value):
                return default

            return float(value)

        except Exception:

            return default

    # ======================================================
    # TREND HELPERS
    # ======================================================

    def last_n(self, history, column, n):
        if column not in history.columns:
            return []

        values = (

            history[column]

            .replace([np.inf, -np.inf], np.nan)

            .dropna()

            .tolist()

        )

        return values[-n:]

    # ------------------------------------------------------

    def consecutive_positive(self, history, column, years):

        values = self.last_n(history, column, years)

        if len(values) < years:
            return False

        return all(v > 0 for v in values)

    # ------------------------------------------------------

    def consecutive_negative(self, history, column, years):

        values = self.last_n(history, column, years)

        if len(values) < years:
            return False

        return all(v < 0 for v in values)

    # ------------------------------------------------------

    # ------------------------------------------------------

    def latest_value(self, latest, *columns, default=np.nan):

        for column in columns:

            if column in latest.index:

                value = latest[column]

                if pd.notna(value):
                    return self.safe_number(value)

        return default
    
    # ------------------------------------------------------

    def deduplicate(self, records):

        seen = set()

        output = []

        for record in records:

            key = (
                record["company_id"],
                record["rule_id"]
            )

            if key not in seen:
                seen.add(key)
                output.append(record)

        return output
    # ------------------------------------------------------

    def validate_company(self, records):

        pros = [
            r for r in records
            if r["type"] == "pro"
        ]

        cons = [
            r for r in records
            if r["type"] == "con"
        ]

        return len(pros), len(cons)
    # ======================================================
    # CASHFLOW HISTORY
    # ======================================================

    def cashflow_history(self, company_id):

        df = self.cashflow[
            self.cashflow.company_id == company_id
        ].copy()

        if "year_num" in df.columns:

            df = df.sort_values("year_num")

        else:

            df = df.sort_values("year")

        return df.reset_index(drop=True)

    # ======================================================
    # OUTPUT RECORD
    # ======================================================

    @staticmethod
    def make_record(

        company_id,
        record_type,
        rule_id,
        text,
        confidence

    ):

        return {

            "company_id": company_id,

            "type": record_type,

            "rule_id": rule_id,

            "text": text,

            "confidence_pct": round(confidence, 1),

        }

    # ======================================================
    # RECORD HELPERS
    # ======================================================

    def add_record(
        self,
        records,
        company_id,
        record_type,
        rule_id,
        text,
        confidence,
    ):
        records.append(
            self.make_record(
                company_id,
                record_type,
                rule_id,
                text,
                confidence,
            )
        )

    # ======================================================
    # CONFIDENCE SCORING
    # ======================================================

    # ======================================================
# DYNAMIC CONFIDENCE ENGINE
# ======================================================

    def confidence_score(self, value, minimum, maximum):
        """
        Dynamic confidence score between 60 and 100.

        Values:
            <= minimum  -> 60
            >= maximum  -> 100
            Between     -> Linear interpolation
        """

        value = self.safe_number(value)

        if maximum <= minimum:
            return 60

        if value <= minimum:
            return 60

        if value >= maximum:
            return 100

        score = 60 + (
            (value - minimum)
            / (maximum - minimum)
        ) * 40

        return round(min(score, 100), 1)

    # ======================================================
    # PRO RULES
    # ======================================================

    def apply_pro_rules(self, company_id):

        records = []

        history = self.company_history(company_id)

        latest = self.latest_row(company_id)

        if latest is None:
            return records

        roe = self.last_n(history, "return_on_equity_pct", 3)
        if len(roe) == 3 and all(x >= 20 for x in roe):
            confidence = self.confidence_score(np.mean(roe), 20, 35)
            self.add_record(
                records,
                company_id,
                "pro",
                "P1",
                "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
                confidence,
            )

        cash_history = self.cashflow_history(company_id)

        fcf = self.last_n(
            cash_history,
            "free_cash_flow_cr",
            5
        )

        if len(fcf) == 5 and all(x > 0 for x in fcf):

            confidence = self.confidence_score(
                np.mean(fcf),
                100,
                5000
            )

            self.add_record(
                records,
                company_id,
                "pro",
                "P2",
                "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
                confidence
            )

        debt = self.safe_number(latest.get("debt_to_equity"), default=np.nan)
        if pd.notna(debt) and debt <= 0.05:
            self.add_record(
                records,
                company_id,
                "pro",
                "P3",
                "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
                95,
            )

        revenue = self.safe_number(latest.get("revenue_cagr_5yr"), default=np.nan)
        if pd.notna(revenue) and revenue >= 15:
            confidence = self.confidence_score(revenue, 15, 35)
            self.add_record(
                records,
                company_id,
                "pro",
                "P4",
                "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum.",
                confidence,
            )

        margin = self.latest_value(
            latest,
            "operating_profit_margin_pct"
        )
        if pd.notna(margin) and margin > 25:
            confidence = min(100, 75 + (margin-25)*1.2)
            self.add_record(
                records,
                company_id,
                "pro",
                "P5",
                "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
                confidence,
            )

        pat = self.safe_number(latest.get("pat_cagr_5yr"), default=np.nan)
        if pd.notna(pat) and pat > 20:
            confidence = min(100, 80 + (pat - 20) * 0.6)
            self.add_record(
                records,
                company_id,
                "pro",
                "P6",
                "Net profit compounding at above 20% over 5 years creates significant shareholder value.",
                confidence,
            )

        icr = self.safe_number(latest.get("interest_coverage"), default=np.nan)
        debt = self.safe_number(latest.get("debt_to_equity"), default=np.nan)
        if (pd.notna(icr) and icr > 10) or (pd.notna(debt) and debt == 0):
            if pd.notna(icr):
                confidence = self.confidence_score(
                    icr,
                    10,
                    30
                )
            else:
                confidence = 95
            self.add_record(
                records,
                company_id,
                "pro",
                "P7",
                "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
                confidence,
            )

        dividend_yield = self.safe_number(latest.get("dividend_yield"), default=np.nan)
        cash_latest = self.cashflow_history(company_id)
        free_cash_flow = np.nan
        if not cash_latest.empty:
            latest_cash = cash_latest.iloc[-1]
            free_cash_flow = self.safe_number(
                latest_cash.get("free_cash_flow_cr")
            )
        if pd.notna(dividend_yield) and pd.notna(free_cash_flow) and dividend_yield > 2 and free_cash_flow > 0:
            confidence = min(100, 70 + dividend_yield * 5)
            self.add_record(
                records,
                company_id,
                "pro",
                "P8",
                "Consistent dividend yield above 2% backed by positive free cash flow.",
                confidence,
            )
        # ==========================================================
        # P9 - EPS CAGR > 15%
        # ==========================================================

        eps_cagr = self.latest_value(
            latest,
            "eps_cagr_5yr",
            "eps_growth_5yr",
            "earnings_per_share_cagr_5yr"
        )

        if pd.notna(eps_cagr) and eps_cagr >= 15:

            confidence = self.confidence_score(
                eps_cagr,
                15,
                35
            )

            self.add_record(
                records,
                company_id,
                "pro",
                "P9",
                "Earnings per share growing above 15% CAGR indicates strong earnings quality and long-term compounding.",
                confidence
            )

        # ==========================================================
        # P10 - ROE Improving
        # ==========================================================

        roe_values = self.last_n(
            history,
            "return_on_equity_pct",
            3
        )

        if len(roe_values) == 3:

            if (
                roe_values[2] > roe_values[1] >
                roe_values[0]
            ):

                confidence = min(
                    100,
                    75 + (
                        roe_values[2] -
                        roe_values[0]
                    ) * 2
                )

                self.add_record(
                    records,
                    company_id,
                    "pro",
                    "P10",
                    "Return on equity improving for three consecutive years reflects strengthening business quality and capital efficiency.",
                    confidence
                )

        # ==========================================================
        # P11 - Operating Leverage
        # ==========================================================

        revenue_cagr = self.latest_value(
            latest,
            "revenue_cagr_5yr"
        )

        pat_cagr = self.latest_value(
            latest,
            "pat_cagr_5yr"
        )

        if (
            pd.notna(revenue_cagr)
            and
            pd.notna(pat_cagr)
        ):

            if pat_cagr > revenue_cagr:

                confidence = min(
                    100,
                    70 + (
                        pat_cagr -
                        revenue_cagr
                    )
                )

                self.add_record(
                    records,
                    company_id,
                    "pro",
                    "P11",
                    "Profits are compounding faster than revenue, indicating improving operating leverage and scalability.",
                    confidence
                )
        # ==========================================================
        # P12 - Assets Growing, Debt Declining
        # ==========================================================

        asset_columns = [
            "total_assets",
            "total_assets_cr",
            "assets"
        ]

        debt_columns = [
            "borrowings",
            "total_borrowings",
            "debt"
        ]

        asset_col = next(
            (
                c for c in asset_columns
                if c in history.columns
            ),
            None
        )

        debt_col = next(
            (
                c for c in debt_columns
                if c in history.columns
            ),
            None
        )

        if asset_col and debt_col:

            assets = self.last_n(
                history,
                asset_col,
                3
            )

            debt = self.last_n(
                history,
                debt_col,
                3
            )

            if (
                len(assets) == 3
                and
                len(debt) == 3
            ):

                if (
                    assets[2] > assets[1] > assets[0]
                    and
                    debt[2] < debt[1] < debt[0]
                ):

                    confidence = 90

                    self.add_record(
                        records,
                        company_id,
                        "pro",
                        "P12",
                        "Growing asset base funded through internal accruals while debt declines reflects disciplined capital allocation.",
                        confidence
                    )

        return records

    # ======================================================
    # CON RULES
    # ======================================================

    def apply_con_rules(self, company_id):

        records = []

        history = self.company_history(company_id)

        latest = self.latest_row(company_id)

        if latest is None:
            return records

        leverage = self.safe_number(latest.get("debt_to_equity"), default=np.nan)
        icr = self.safe_number(latest.get("interest_coverage"), default=np.nan)
        margin = self.latest_value(
            latest,
            "operating_profit_margin_pct"
        )
        revenue = self.safe_number(latest.get("revenue_cagr_5yr"), default=np.nan)
        free_cash_flow = self.safe_number(latest.get("free_cash_flow_cr"), default=np.nan)

        if pd.notna(leverage) and leverage > 2:
            confidence = min(100, 70 + (leverage - 2) * 10)
            self.add_record(
                records,
                company_id,
                "con",
                "C1",
                "High leverage relative to equity can restrict future capital flexibility.",
                confidence,
            )

        if pd.notna(icr) and icr <= 2:
            confidence = min(100, self.confidence_score(
                3-icr,
                1,
                5
            ))
            self.add_record(
                records,
                company_id,
                "con",
                "C2",
                "Low interest coverage indicates potential difficulty servicing debt if earnings fall.",
                confidence,
            )

        

        if pd.notna(margin) and margin < 10:
            confidence = min(100, 70 + (10 - margin) * 2)
            self.add_record(
                records,
                company_id,
                "con",
                "C3",
                "Weak operating margins suggest limited pricing power and lower cash generation.",
                confidence,
            )

        if pd.notna(revenue) and revenue < 5:
            confidence = min(100, 65 + (5 - revenue) * 3)
            self.add_record(
                records,
                company_id,
                "con",
                "C4",
                "Low revenue growth may indicate a lack of business momentum.",
                confidence,
            )

        cash_history = self.cashflow_history(company_id)

        if self.consecutive_negative(
                cash_history,
                "free_cash_flow_cr",
                2
        ):
            self.add_record(
                records,
                company_id,
                "con",
                "C5",
                "Two consecutive years of negative free cash flow point to weak cash generation.",
                80,
            )

        # ==========================================================
        # C6 - Net Loss
        # ==========================================================

        net_profit = self.latest_value(
            latest,
            "net_profit_cr",
            "profit_after_tax_cr",
            "pat_cr"
        )

        if pd.notna(net_profit) and net_profit < 0:

            self.add_record(
                records,
                company_id,
                "con",
                "C6",
                "Company reported a net loss in the latest financial year.",
                95
            )

        # ==========================================================
        # C7 - Dividend Payout >100%
        # ==========================================================

        payout = self.latest_value(
            latest,
            "dividend_payout_ratio_pct",
            "dividend_payout_pct",
            "dividend_payout_ratio"
        )

        if pd.notna(payout) and payout > 100:

            confidence = self.confidence_score(
                payout,
                100,
                200
            )

            self.add_record(
                records,
                company_id,
                "con",
                "C7",
                "Dividend payout above 100% indicates dividends may be funded from reserves and could be unsustainable.",
                confidence
            )

        # ==========================================================
        # C8 - Rising Debt
        # ==========================================================

        debt_history = self.last_n(
            history,
            "debt_to_equity",
            3
        )

        if len(debt_history) == 3:

            if (
                debt_history[2] >
                debt_history[1] >
                debt_history[0]
            ):

                self.add_record(
                    records,
                    company_id,
                    "con",
                    "C8",
                    "Debt-to-equity ratio has increased continuously for three years, indicating rising financial leverage.",
                    85
                )

        # ==========================================================
        # C9 - EPS Declining
        # ==========================================================

        eps_columns = [
            "eps",
            "earnings_per_share",
            "eps_basic"
        ]

        eps_column = next(
            (
                c for c in eps_columns
                if c in history.columns
            ),
            None
        )

        if eps_column:

            eps = self.last_n(
                history,
                eps_column,
                3
            )

            if (
                len(eps) == 3
                and
                eps[2] < eps[1] < eps[0]
            ):

                self.add_record(
                    records,
                    company_id,
                    "con",
                    "C9",
                    "Earnings per share have declined for three consecutive years, indicating weakening profitability.",
                    88
                )

        # ==========================================================
        # C10 - Low ROCE
        # ==========================================================

        roce = self.latest_value(
            latest,
            "return_on_capital_employed_pct",
            "roce"
        )

        if pd.notna(roce) and roce < 10:

            confidence = self.confidence_score(
                10 - roce,
                0,
                10
            )

            self.add_record(
                records,
                company_id,
                "con",
                "C10",
                "Return on capital employed below 10% indicates weak capital efficiency.",
                confidence
            )

        # ==========================================================
        # C11 - Net Debt / EBITDA
        # ==========================================================

        net_debt = self.latest_value(
            latest,
            "net_debt_cr",
            "net_debt"
        )

        ebitda = self.latest_value(
            latest,
            "ebitda_cr",
            "ebitda"
        )

        if (
            pd.notna(net_debt)
            and
            pd.notna(ebitda)
            and
            ebitda > 0
        ):

            ratio = net_debt / ebitda

            if ratio > 3:

                confidence = self.confidence_score(
                    ratio,
                    3,
                    8
                )

                self.add_record(
                    records,
                    company_id,
                    "con",
                    "C11",
                    f"Net debt is {ratio:.1f}× EBITDA, indicating elevated leverage.",
                    confidence
                )

        # ==========================================================
        # C12 - Revenue Declining
        # ==========================================================

        revenue_columns = [
            "sales_cr",
            "revenue_cr",
            "total_income_cr"
        ]

        revenue_column = next(
            (
                c for c in revenue_columns
                if c in history.columns
            ),
            None
        )

        if revenue_column:

            revenue = self.last_n(
                history,
                revenue_column,
                3
            )

            if (
                len(revenue) == 3
                and
                revenue[2] < revenue[1]
                and
                revenue[1] < revenue[0]
            ):

                self.add_record(
                    records,
                    company_id,
                    "con",
                    "C12",
                    "Revenue has declined for multiple consecutive years, indicating weakening business momentum.",
                    85
                )

        return records

    # ======================================================
    # REPORT GENERATION
    # ======================================================

    def generate_records(self):

        records = []

        company_ids = (
            self.companies["company_id"]
            .drop_duplicates()
            .tolist()
        )

        print(f"\nProcessing {len(company_ids)} companies...\n")

        for company_id in company_ids:

            company_records = []

            company_records.extend(
                self.apply_pro_rules(company_id)
            )

            company_records.extend(
                self.apply_con_rules(company_id)
            )

            company_records = self.deduplicate(
                company_records
            )

            pros, cons = self.validate_company(company_records)

            if pros == 0:
                self.add_record(
                    company_records,
                    company_id,
                    "pro",
                    "P_FALLBACK",
                    "The company continues to operate with stable financial performance and remains suitable for ongoing monitoring.",
                    65
                )

            if cons == 0:
                self.add_record(
                    company_records,
                    company_id,
                    "con",
                    "C_FALLBACK",
                    "No major financial weakness was identified by the rule engine, although ongoing monitoring remains important.",
                    65
                )
            
            records.extend(company_records)

        return pd.DataFrame(
            records,
            columns=[
                "company_id",
                "type",
                "rule_id",
                "text",
                "confidence_pct",
            ],
        )
    
    # ======================================================
    # VALIDATION
    # ======================================================

    def validate_output(self, report):

        print("\n" + "=" * 60)
        print("VALIDATING GENERATED PROS / CONS")
        print("=" * 60)

        summary = (
            report.groupby(["company_id", "type"])
            .size()
            .unstack(fill_value=0)
        )

        if "pro" not in summary.columns:
            summary["pro"] = 0

        if "con" not in summary.columns:
            summary["con"] = 0

        missing_pro = summary[summary["pro"] == 0]
        missing_con = summary[summary["con"] == 0]

        print(f"\nCompanies Processed : {len(summary)}")
        print(f"Total Pros          : {report[report.type=='pro'].shape[0]}")
        print(f"Total Cons          : {report[report.type=='con'].shape[0]}")

        print(f"\nMissing Pros : {len(missing_pro)}")
        print(f"Missing Cons : {len(missing_con)}")

        if len(missing_pro):

            print("\nCompanies Missing Pro")

            print(missing_pro.index.tolist())

        if len(missing_con):

            print("\nCompanies Missing Con")

            print(missing_con.index.tolist())

        if len(missing_pro) == 0 and len(missing_con) == 0:

            print("\nSUCCESS")
            print("Every company has at least one Pro and one Con.")

        return summary

    # ======================================================
    # RULE STATISTICS
    # ======================================================

    def rule_statistics(self, report):

        print("\n" + "=" * 60)
        print("RULE DISTRIBUTION")
        print("=" * 60)

        stats = (
            report.groupby("rule_id")
            .size()
            .sort_values(ascending=False)
        )

        print(stats)

        return stats

    # ======================================================
    # COMPANY SUMMARY
    # ======================================================

    def company_statistics(self, report):

        print("\n" + "=" * 60)
        print("COMPANY SUMMARY")
        print("=" * 60)

        summary = (
            report.groupby("company_id")
            .size()
            .sort_values(ascending=False)
        )

        print(summary.describe())

        return summary
    
    def generate_csv(self, output_file=OUTPUT_FILE):
        try:
            print("\nGenerating Pros & Cons...")

            report = self.generate_records()

            report["order"] = report["type"].map(
                {"pro":0,"con":1}
            )

            report = report.sort_values(
                ["company_id","order","rule_id"]
            ).drop(columns="order")

            report.to_csv(
                output_file,
                index=False
            )

            print("\nCSV Saved")

            print(output_file)

            self.validate_output(report)

            self.rule_statistics(report)

            self.company_statistics(report)

            self.export_validation(report)

            return report

        finally:
            self.conn.close()
    
    # ======================================================
    # EXPORT VALIDATION
    # ======================================================

    def export_validation(self, report):

        validation = (
            report.groupby(
                ["company_id", "type"]
            )
            .size()
            .unstack(fill_value=0)
        )

        validation.to_csv(
            OUTPUT_DIR /
            "pros_cons_validation.csv"
        )

        print(
            "\nValidation Report Saved"
        )

if __name__ == "__main__":

    generator = ProsConsGenerator()

    report = generator.generate_csv()
    

    print("\nSprint 5 NLP Module Completed Successfully.")