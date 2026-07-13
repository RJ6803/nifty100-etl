from pathlib import Path
import pandas as pd


class PortfolioExporter:
    """
    Exports portfolio allocation and portfolio metrics
    into a multi-sheet Excel workbook.
    """

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        portfolio_df: pd.DataFrame,
        metrics: dict,
        filename: str = "Portfolio_Report.xlsx",
    ):
        """
        Parameters
        ----------
        portfolio_df : DataFrame
            Portfolio allocation dataframe.

        metrics : dict
            Dictionary returned from PortfolioMetrics.calculate()

        filename : str
            Output Excel filename.
        """

        filepath = self.output_dir / filename

        # Convert metrics dictionary into dataframe
        metrics_df = pd.DataFrame(
            {
                "Metric": list(metrics.keys()),
                "Value": list(metrics.values()),
            }
        )

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:

            # Portfolio Sheet

            portfolio_df.to_excel(
                writer,
                sheet_name="Portfolio",
                index=False,
            )


            # Metrics Sheet

            metrics_df.to_excel(
                writer,
                sheet_name="Portfolio Metrics",
                index=False,
            )


            # Formatting

            for sheet in writer.sheets.values():
                for column_cells in sheet.columns:
                    length = max(
                        len(str(cell.value)) if cell.value is not None else 0
                        for cell in column_cells
                    )
                    sheet.column_dimensions[
                        column_cells[0].column_letter
                    ].width = length + 4

        print(f"\nPortfolio exported successfully.")
        print(f"Location : {filepath.resolve()}")

        return filepath