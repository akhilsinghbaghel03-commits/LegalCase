import os
import sys
import xml.etree.ElementTree as ET

# Ensure openpyxl is available, auto-installing if running on an environment without it
try:
    from openpyxl import Workbook
except ImportError:
    import subprocess
    print("openpyxl not found. Installing openpyxl...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    from openpyxl import Workbook


XML_FILE = "reports/results.xml"
EXCEL_FILE = "reports/Test-Execution-Report.xlsx"


def generate_excel_report():
    if not os.path.exists(XML_FILE):
        print(f"ERROR: {XML_FILE} not found")
        return 1

    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    workbook = Workbook()

    summary = workbook.active
    summary.title = "Execution Summary"

    results = workbook.create_sheet("Test Results")

    # Summary header
    summary.append(["Metric", "Value"])

    # Test results header
    results.append([
        "Test Case",
        "Class",
        "Status",
        "Duration"
    ])

    tests = 0
    failures = 0
    errors = 0
    skipped = 0
    passed = 0

    for testcase in root.iter("testcase"):
        tests += 1
        name = testcase.attrib.get("name", "")
        classname = testcase.attrib.get("classname", "")
        duration = testcase.attrib.get("time", "0")

        if testcase.find("failure") is not None:
            status = "FAIL"
            failures += 1
        elif testcase.find("error") is not None:
            status = "ERROR"
            errors += 1
        elif testcase.find("skipped") is not None:
            status = "SKIPPED"
            skipped += 1
        else:
            status = "PASS"
            passed += 1

        results.append([
            name,
            classname,
            status,
            duration
        ])

    summary.append(["Total Tests", tests])
    summary.append(["Passed", passed])
    summary.append(["Failed", failures])
    summary.append(["Errors", errors])
    summary.append(["Skipped", skipped])

    # Auto-adjust column width
    for sheet in workbook.worksheets:
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            sheet.column_dimensions[column_letter].width = min(
                max_length + 2,
                60
            )

    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)
    workbook.save(EXCEL_FILE)

    print(f"Excel report generated: {EXCEL_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_excel_report())
