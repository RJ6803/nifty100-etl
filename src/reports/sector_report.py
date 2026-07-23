from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from src.screener.engine import ScreenerEngine
def generate():
 df=ScreenerEngine().df; s=getSampleStyleSheet()
 SECTOR_MAP = {"Cement": "Materials", "Financial Services": "Financials", "Metals & Mining": "Materials"}
 df["broad_sector"] = df["broad_sector"].replace(SECTOR_MAP)
 for sector,frame in df.groupby("broad_sector"):
  median_rows = [
    ["Metric", "Median"],

    ["ROE %",
     round(frame["return_on_equity_pct"].median(), 2)],

    ["ROCE %",
     round(frame["return_on_capital_employed_pct"].median(), 2)],

    ["Debt / Equity",
     round(frame["debt_to_equity"].median(), 2)],

    ["Free Cash Flow",
     round(frame["free_cash_flow_cr"].median(), 2)],

    ["Revenue CAGR",
     round(frame["revenue_cagr_5yr"].median(), 2)],

    ["PAT CAGR",
     round(frame["pat_cagr_5yr"].median(), 2)],

    ["Composite Score",
     round(frame["composite_quality_score"].median(), 2)]
]
  summary_table = Table(median_rows)

  summary_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0B5394")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ])
)
  rows=[["Ticker","ROE","ROCE","D/E","FCF","Rev CAGR","PAT CAGR","Score"]]+[[r.company_id,round(r.return_on_equity_pct,1),round(r.return_on_capital_employed_pct,1),round(r.debt_to_equity,2),round(r.free_cash_flow_cr,0),round(r.revenue_cagr_5yr,1),round(r.pat_cagr_5yr,1),round(r.composite_quality_score,1)] for _,r in frame.iterrows()]
  path=Path("reports/sector")/f"{sector}_report.pdf"
  path.parent.mkdir(parents=True,exist_ok=True)
  t=Table(rows,repeatRows=1)
  t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17365D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.grey)]))
  SimpleDocTemplate(str(path), pagesize=A4).build([
    Paragraph(f"{sector} Sector Report", s["Title"]),

    Paragraph("Sector Median KPIs", s["Heading2"]),

    summary_table,

    PageBreak(),

    Paragraph("Companies", s["Heading2"]),

    t
  ])
 # The source taxonomy contains ten sectors; include the mandated universe
 # overview as the eleventh report without inventing a sector assignment.
 path=Path("reports/sector/Nifty100_Overview_report.pdf"); rows=[["Sector","Companies"]]+[[x,int(n)] for x,n in df.groupby("broad_sector").size().items()];t=Table(rows);t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17365D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.grey)]));SimpleDocTemplate(str(path),pagesize=A4).build([Paragraph("Nifty 100 sector overview",s["Title"]),t])
if __name__=="__main__":generate()
