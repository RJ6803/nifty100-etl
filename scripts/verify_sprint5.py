import os
import sqlite3
import pandas as pd
from pathlib import Path

def run_verification():
    print("=" * 60)
    print("SPRINT 5 VERIFICATION SUITE")
    print("=" * 60)

    db_path = "data/nifty100.db"
    conn = sqlite3.connect(db_path)
    db_companies = pd.read_sql("SELECT id FROM companies", conn)["id"].tolist()
    conn.close()

    print(f"Target Universe: {len(db_companies)} companies in nifty100.db\n")

    # 1. NLP Parser Outputs
    print("[1/8] Verifying NLP Analysis Text Parser...")
    parsed_file = Path("output/analysis_parsed.csv")
    fail_file = Path("output/parse_failures.csv")
    cagr_val_file = Path("output/analysis_cagr_cross_validation.csv")

    assert parsed_file.exists(), "analysis_parsed.csv missing!"
    df_parsed = pd.read_csv(parsed_file)
    print(f"  - analysis_parsed.csv: {len(df_parsed)} rows parsed.")
    assert set(["company_id", "metric_type", "period_years", "value_pct"]).issubset(df_parsed.columns)

    assert fail_file.exists(), "parse_failures.csv missing!"
    assert cagr_val_file.exists(), "analysis_cagr_cross_validation.csv missing!"
    print("  [OK] NLP Parser outputs verified.")

    # 2. Pros / Cons Generated
    print("\n[2/8] Verifying Auto Pros/Cons Generator...")
    pros_cons_file = Path("output/pros_cons_generated.csv")
    assert pros_cons_file.exists(), "pros_cons_generated.csv missing!"
    df_pc = pd.read_csv(pros_cons_file)
    print(f"  - Total generated entries: {len(df_pc)}")
    assert set(["company_id", "type", "rule_id", "text", "confidence_pct"]).issubset(df_pc.columns)
    assert (df_pc["confidence_pct"] > 60).all(), "Found entries with confidence <= 60%"

    missing_pros = []
    missing_cons = []
    for cid in db_companies:
        sub = df_pc[df_pc["company_id"] == cid]
        if (sub["type"] == "pro").sum() == 0:
            missing_pros.append(cid)
        if (sub["type"] == "con").sum() == 0:
            missing_cons.append(cid)

    print(f"  - Companies missing Pros: {len(missing_pros)}")
    print(f"  - Companies missing Cons: {len(missing_cons)}")
    assert len(missing_pros) == 0 and len(missing_cons) == 0, "Not all companies have >=1 pro and >=1 con!"
    print("  [OK] Pros/Cons Generator verified.")

    # 3. Cashflow Intelligence
    print("\n[3/8] Verifying Cash Flow Intelligence Module...")
    cf_file = Path("output/cashflow_intelligence.xlsx")
    assert cf_file.exists(), "cashflow_intelligence.xlsx missing!"
    df_cf = pd.read_excel(cf_file)
    print(f"  - Rows in cashflow_intelligence.xlsx: {len(df_cf)}")
    assert len(df_cf) == 92, f"Expected 92 rows in cashflow_intelligence.xlsx, got {len(df_cf)}"
    req_cols = ["company_id", "sector", "cfo_quality_score", "cfo_quality_label", "capex_intensity_pct", "capex_label", "fcf_cagr_5yr", "fcf_conversion_pct", "distress_flag", "deleveraging_flag", "capital_allocation_label"]
    assert set(req_cols).issubset(df_cf.columns), f"Missing required columns in cashflow_intelligence.xlsx! {set(req_cols) - set(df_cf.columns)}"

    distress_file = Path("output/distress_alerts.csv")
    assert distress_file.exists(), "distress_alerts.csv missing!"
    print("  [OK] Cash Flow Intelligence verified.")

    # 4. Pattern Changes
    print("\n[4/8] Verifying Capital Allocation Pattern Changes...")
    pattern_file = Path("output/pattern_changes.csv")
    assert pattern_file.exists(), "pattern_changes.csv missing!"
    df_pat = pd.read_csv(pattern_file)
    print(f"  - Pattern changes recorded: {len(df_pat)}")
    print("  [OK] Capital Allocation report outputs verified.")

    # 5. Company Tearsheets
    print("\n[5/8] Verifying Company Tearsheets...")
    ts_dir = Path("reports/tearsheets")
    ts_files = list(ts_dir.glob("*_tearsheet.pdf"))
    print(f"  - Total tearsheet PDFs found: {len(ts_files)}")

    skipped_file = Path("output/skipped_tearsheets.csv")
    skipped_count = 0
    if skipped_file.exists():
        df_skip = pd.read_csv(skipped_file)
        skipped_count = len(df_skip)
        print(f"  - Skipped tearsheets logged: {skipped_count}")

    # Check size of each tearsheet
    small_files = [f for f in ts_files if f.stat().st_size < 30 * 1024]
    print(f"  - Tearsheets smaller than 30KB: {len(small_files)}")
    assert len(small_files) == 0, f"Found tearsheets under 30KB: {small_files}"
    assert len(ts_files) >= 92 - skipped_count, f"Expected at least {92 - skipped_count} tearsheet PDFs!"
    print("  [OK] Tearsheet PDFs verified.")

    # 6. Sector PDFs
    print("\n[6/8] Verifying Sector PDF Reports...")
    sector_dir = Path("reports/sector")
    sector_files = list(sector_dir.glob("*.pdf"))
    print(f"  - Total sector PDFs found: {len(sector_files)}")
    assert len(sector_files) == 11, f"Expected 11 sector PDFs, found {len(sector_files)}"
    print("  [OK] Sector PDF Reports verified.")

    # 7. Portfolio Summary PDF
    print("\n[7/8] Verifying Portfolio Summary PDF...")
    port_pdf = Path("reports/portfolio/portfolio_summary.pdf")
    assert port_pdf.exists(), "portfolio_summary.pdf missing!"
    assert port_pdf.stat().st_size > 10 * 1024, "portfolio_summary.pdf is too small!"
    print(f"  - portfolio_summary.pdf size: {port_pdf.stat().st_size / 1024:.1f} KB")
    print("  [OK] Portfolio Summary PDF verified.")

    print("\n" + "=" * 60)
    print("ALL SPRINT 5 EXIT CRITERIA MET SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
