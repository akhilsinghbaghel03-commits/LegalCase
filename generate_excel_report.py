"""
generate_excel_report.py - Entry point for automated report generation.
Generates both the advanced 4-sheet Excel report and responsive HTML report.
"""

import sys
import os

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.report_generator import ReportGenerator


def main():
    source_file = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "reports"

    try:
        generator = ReportGenerator(source_path=source_file, output_dir=output_dir)
        excel_path, html_path = generator.generate_all_reports()
        print(f"\n==================================================")
        print(f"[REPORT GENERATION COMPLETED]")
        print(f"  - Total Tests:     {generator.total_tests}")
        print(f"  - Passed:          {generator.passed_tests}")
        print(f"  - Failed:          {generator.failed_tests}")
        print(f"  - Skipped:         {generator.skipped_tests}")
        print(f"  - Overall Status:  {generator.overall_status}")
        print(f"  - Excel Report:    {excel_path}")
        print(f"  - HTML Report:     {html_path}")
        print(f"==================================================")
        return 0
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to generate reports: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
