@echo off
setlocal EnableDelayedExpansion

echo ===============================================================================
echo                LEGALHUB AUTOMATION TEST EXECUTION
echo ===============================================================================

:: 1. Change directory to %WORKSPACE% if defined (Jenkins workspace)
if defined WORKSPACE (
    echo [INFO] Changing directory to Jenkins WORKSPACE: "%WORKSPACE%"
    cd /d "%WORKSPACE%"
    if errorlevel 1 (
        echo [ERROR] Failed to change directory to WORKSPACE.
        exit /b 1
    )
) else (
    echo [INFO] WORKSPACE variable not defined. Using current directory: "%CD%"
)

:: Define Python path (Python 3.13)
set "PYTHON_EXE=C:\Program Files\Python313\python.exe"

:: 2. Verify that Python exists at C:\Program Files\Python313\python.exe
echo.
echo [STEP 1/6] Verifying Python installation...
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found at: "%PYTHON_EXE%"
    echo [ERROR] Please verify that Python 3.13 is installed on this Windows node.
    exit /b 1
)
echo [SUCCESS] Found Python executable: "%PYTHON_EXE%"
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo [ERROR] Failed to execute Python executable.
    exit /b 1
)

:: 3. Verify/install pip using ensurepip
echo.
echo [STEP 2/6] Verifying and setting up pip via ensurepip...
"%PYTHON_EXE%" -m ensurepip --upgrade
if errorlevel 1 (
    echo [ERROR] Failed to initialize pip using ensurepip.
    exit /b 1
)

:: 4. Upgrade pip
echo.
echo [STEP 3/6] Upgrading pip to latest version...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    exit /b 1
)

:: 5. Install all dependencies from requirements.txt
echo.
echo [STEP 4/6] Installing dependencies from requirements.txt...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in "%CD%"
    exit /b 1
)
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    exit /b 1
)
echo [SUCCESS] All dependencies installed successfully.

:: 6. Clean and recreate reports folder
echo.
echo [STEP 5/6] Resetting reports directory...
if exist "reports" (
    echo [INFO] Removing existing reports folder...
    rmdir /s /q "reports"
)
mkdir "reports"
if not exist "reports" (
    echo [ERROR] Failed to create reports folder.
    exit /b 1
)
echo [SUCCESS] Fresh reports directory created at "%CD%\reports".

:: 7. Run pytest
echo.
echo [STEP 6/6] Executing Pytest Test Suite...
echo [INFO] Command: "%PYTHON_EXE%" -m pytest --junitxml=reports/results.xml --html=reports/report.html --self-contained-html --ignore=test_contact_out.txt -v
"%PYTHON_EXE%" -m pytest --junitxml=reports/results.xml --html=reports/report.html --self-contained-html --ignore=test_contact_out.txt -v
set "PYTEST_EXIT_CODE=%ERRORLEVEL%"

echo.
echo ===============================================================================
if %PYTEST_EXIT_CODE% equ 0 (
    echo [INFO] Pytest execution completed successfully (Exit Code: 0).
) else (
    echo [WARNING] Pytest execution finished with exit code: %PYTEST_EXIT_CODE% (Test failure or error).
)
echo ===============================================================================

:: 8. Run generate_excel_report.py after the tests
echo.
echo [POST-TEST] Generating Excel Test Execution Report...
if exist "generate_excel_report.py" (
    "%PYTHON_EXE%" generate_excel_report.py
    set "EXCEL_EXIT_CODE=%ERRORLEVEL%"
    if !EXCEL_EXIT_CODE! neq 0 (
        echo [ERROR] Excel report generation failed with exit code: !EXCEL_EXIT_CODE!
    ) else (
        echo [SUCCESS] Excel report generated successfully at reports/Test-Execution-Report.xlsx.
    )
) else (
    echo [WARNING] generate_excel_report.py not found. Skipping Excel report generation.
    set "EXCEL_EXIT_CODE=0"
)

:: 9. Summary & Exit Code Handling
echo.
echo ===============================================================================
echo                       EXECUTION SUMMARY
echo ===============================================================================
echo Pytest Exit Code:       %PYTEST_EXIT_CODE%
echo Excel Report Exit Code: %EXCEL_EXIT_CODE%
echo ===============================================================================

:: Return non-zero if tests failed
if %PYTEST_EXIT_CODE% neq 0 (
    echo [EXIT] Exiting with Pytest exit code %PYTEST_EXIT_CODE% so Jenkins identifies the test failure.
    exit /b %PYTEST_EXIT_CODE%
)

:: Return non-zero if Excel report failed
if %EXCEL_EXIT_CODE% neq 0 (
    echo [EXIT] Exiting with Excel generator exit code %EXCEL_EXIT_CODE%.
    exit /b %EXCEL_EXIT_CODE%
)

echo [EXIT] All steps completed successfully with exit code 0.
exit /b 0
