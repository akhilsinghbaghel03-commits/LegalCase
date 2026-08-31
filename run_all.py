import time
import datetime
import subprocess
import sys

if __name__ == "__main__":
    # Run run_signup.py
    print("\n\n=== RUNNING: run_signup.py ===")
    subprocess.run([sys.executable, "test/run_signup.py"], check=False)
    
    # Run pytest files in exact sequence requested, generating reports
    print("\n\n=== RUNNING: pytest sequence ===")
    pytest_cmd = [
        sys.executable, "-m", "pytest", 
        "test/test_registration.py", 
        "test/test_forgot_password.py", 
        "test/test_login_scenarios.py", 
        "test/test_contact.py",
        "test/test_matter.py",
        "-v", "-s", 
        "--html=report.html", 
        "--excelreport=report.xlsx"
    ]
    subprocess.run(pytest_cmd, check=False)
    print("Done!")
