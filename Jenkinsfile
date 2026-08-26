pipeline {
    agent any

    options {
        timeout(time: 90, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    triggers {
        githubPush()
    }

    environment {
        PROJECT_NAME    = 'Legalhub Automation'
        RECIPIENT_EMAIL = 'akhilsinghbaghel03@gmail.com'
        PYTHON_EXE      = 'C:\\Program Files\\Python313\\python.exe'
    }

    stages {
        stage('Prepare Environment') {
            steps {
                bat """
                    @echo off
                    echo ===============================================================================
                    echo [STEP 1/4] Verifying Python 3.13 Installation
                    echo ===============================================================================
                    if not exist "${PYTHON_EXE}" (
                        echo [ERROR] Python executable not found at: "${PYTHON_EXE}"
                        exit /b 1
                    )
                    "${PYTHON_EXE}" --version
                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===============================================================================
                    echo [STEP 2/4] Setting up pip via ensurepip and upgrading
                    echo ===============================================================================
                    "${PYTHON_EXE}" -m ensurepip --upgrade
                    if errorlevel 1 exit /b 1

                    "${PYTHON_EXE}" -m pip install --upgrade pip
                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===============================================================================
                    echo [STEP 3/4] Installing dependencies from requirements.txt
                    echo ===============================================================================
                    if not exist "requirements.txt" (
                        echo [ERROR] requirements.txt not found in workspace!
                        exit /b 1
                    )
                    "${PYTHON_EXE}" -m pip install -r requirements.txt
                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===============================================================================
                    echo [STEP 4/4] Resetting reports directory
                    echo ===============================================================================
                    if exist "reports" rmdir /s /q "reports"
                    mkdir "reports"
                    if not exist "reports" (
                        echo [ERROR] Failed to create reports folder!
                        exit /b 1
                    )
                    echo [SUCCESS] Reports directory initialized.
                """
            }
        }

        stage('Execute Automation Tests') {
            steps {
                script {
                    echo "==============================================================================="
                    echo "[STEP 5] Running Pytest Automation Test Suite"
                    echo "==============================================================================="

                    // Execute pytest and capture exit code safely to allow Excel generation before failing
                    env.PYTEST_EXIT_CODE = bat(
                        script: """
                            @echo off
                            "${PYTHON_EXE}" -m pytest --junitxml=reports/results.xml --html=reports/report.html --self-contained-html --ignore=test_contact_out.txt -v
                        """,
                        returnStatus: true
                    ).toString()

                    echo "Pytest execution finished with exit code: ${env.PYTEST_EXIT_CODE}"
                }
            }
        }

        stage('Generate Excel Report') {
            steps {
                script {
                    echo "==============================================================================="
                    echo "[STEP 6] Generating Excel Test Execution Report"
                    echo "==============================================================================="

                    // 1. Verify generate_excel_report.py exists
                    def scriptExists = fileExists 'generate_excel_report.py'
                    if (!scriptExists) {
                        error("[ERROR] generate_excel_report.py was not found in the workspace!")
                    }

                    // 2. Run Excel report generator
                    def excelStatus = bat(
                        script: """
                            @echo off
                            "${PYTHON_EXE}" generate_excel_report.py
                        """,
                        returnStatus: true
                    )

                    if (excelStatus != 0) {
                        error("[ERROR] generate_excel_report.py failed with exit code: ${excelStatus}")
                    }
                    echo "[SUCCESS] Excel report generated at reports/Test-Execution-Report.xlsx"

                    // 3. If pytest failed earlier, fail this stage now so Jenkins marks the build result accurately
                    if (env.PYTEST_EXIT_CODE != "0") {
                        error("[FAILURE] Pytest automation suite encountered test failure(s) (Exit Code: ${env.PYTEST_EXIT_CODE}).")
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                echo "==============================================================================="
                echo "[STEP 7] Publishing Test Reports & Artifacts"
                echo "==============================================================================="

                // 1. JUnit XML Test Results
                junit testResults: 'reports/results.xml', allowEmptyResults: true

                // 2. HTML Publisher Plugin
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'HTML Automation Report'
                ])

                // 3. Archive all reports
                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                // Ensure reports and test results are always published even if earlier stages failed
                junit testResults: 'reports/results.xml', allowEmptyResults: true

                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'HTML Automation Report'
                ])

                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            }
        }

        success {
            script {
                try {
                    emailext (
                        to: env.RECIPIENT_EMAIL,
                        subject: "SUCCESS: ${env.PROJECT_NAME} - Build #${env.BUILD_NUMBER}",
                        body: """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
                                .container { max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e1e4e8; }
                                .header { background: #1a237e; color: #ffffff; padding: 22px; text-align: center; }
                                .header h1 { margin: 0; font-size: 22px; }
                                .header p { margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }
                                .content { padding: 24px; }
                                .status-banner { text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 6px; font-size: 18px; font-weight: bold; color: #ffffff; background-color: #28a745; }
                                .table-info, .table-summary { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                                .table-info td { padding: 8px 12px; border-bottom: 1px solid #edf2f7; font-size: 14px; }
                                .table-info td.label { font-weight: 600; color: #4a5568; width: 35%; }
                                .table-summary th, .table-summary td { padding: 10px; text-align: center; border: 1px solid #e2e8f0; font-size: 14px; }
                                .table-summary th { background-color: #f7fafc; color: #4a5568; font-weight: 600; }
                                .stat-pass { color: #28a745; font-weight: bold; }
                                .stat-fail { color: #dc3545; font-weight: bold; }
                                .stat-skip { color: #ffc107; font-weight: bold; }
                                .box { background-color: #f8f9fa; border-left: 4px solid #1a237e; padding: 14px 18px; border-radius: 4px; margin-bottom: 20px; }
                                .box h4 { margin: 0 0 8px 0; color: #1a237e; font-size: 15px; }
                                .box ul { margin: 0; padding-left: 20px; font-size: 13px; color: #555; }
                                .btn-container { text-align: center; margin: 25px 0 10px 0; }
                                .btn { background-color: #0d6efd; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block; }
                                .footer { background: #fafafa; padding: 16px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #edf2f7; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>${env.PROJECT_NAME}</h1>
                                    <p>Automated Test Execution Summary</p>
                                </div>
                                <div class="content">
                                    <div class="status-banner">
                                        BUILD SUCCESS
                                    </div>
                                    <table class="table-info">
                                        <tr>
                                            <td class="label">Job Name:</td>
                                            <td>${env.JOB_NAME}</td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build Number:</td>
                                            <td>#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build Status:</td>
                                            <td><strong style="color: #28a745;">SUCCESS</strong></td>
                                        </tr>
                                        <tr>
                                            <td class="label">Git Commit:</td>
                                            <td><code>${env.GIT_COMMIT ?: 'Latest master'}</code></td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build URL:</td>
                                            <td><a href="${env.BUILD_URL}" style="color: #0d6efd;">${env.BUILD_URL}</a></td>
                                        </tr>
                                        <tr>
                                            <td class="label">HTML Report:</td>
                                            <td><a href="${env.BUILD_URL}HTML_20Automation_20Report/" style="color: #0d6efd;">View HTML Report</a></td>
                                        </tr>
                                    </table>

                                    <h3 style="color: #2d3748; font-size: 16px; margin-bottom: 10px;">Test Report Summary</h3>
                                    <table class="table-summary">
                                        <thead>
                                            <tr>
                                                <th>Total Tests</th>
                                                <th>Passed</th>
                                                <th>Failed</th>
                                                <th>Skipped</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td><strong>\${TEST_COUNTS, var="total"}</strong></td>
                                                <td class="stat-pass">\${TEST_COUNTS, var="pass"}</td>
                                                <td class="stat-fail">\${TEST_COUNTS, var="fail"}</td>
                                                <td class="stat-skip">\${TEST_COUNTS, var="skip"}</td>
                                            </tr>
                                        </tbody>
                                    </table>

                                    <div class="box">
                                        <h4>Attached Reports:</h4>
                                        <ul>
                                            <li><strong>HTML Report:</strong> <code>report.html</code></li>
                                            <li><strong>Excel Execution Report:</strong> <code>Test-Execution-Report.xlsx</code></li>
                                            <li><strong>JUnit XML Results:</strong> <code>results.xml</code></li>
                                        </ul>
                                    </div>

                                    <div class="btn-container">
                                        <a href="${env.BUILD_URL}" class="btn">Open Jenkins Build</a>
                                    </div>
                                </div>
                                <div class="footer">
                                    This email was automatically generated by Jenkins CI/CD.
                                </div>
                            </div>
                        </body>
                        </html>
                        """,
                        mimeType: 'text/html',
                        attachmentsPattern: 'reports/*.html, reports/*.xlsx, reports/*.xml',
                        attachLog: false
                    )
                } catch (Exception e) {
                    echo "[WARNING] Success email notification failed: ${e.message}"
                }
            }
        }

        failure {
            script {
                try {
                    emailext (
                        to: env.RECIPIENT_EMAIL,
                        subject: "FAILURE: ${env.PROJECT_NAME} - Build #${env.BUILD_NUMBER}",
                        body: """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
                                .container { max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e1e4e8; }
                                .header { background: #b71c1c; color: #ffffff; padding: 22px; text-align: center; }
                                .header h1 { margin: 0; font-size: 22px; }
                                .header p { margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }
                                .content { padding: 24px; }
                                .status-banner { text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 6px; font-size: 18px; font-weight: bold; color: #ffffff; background-color: #dc3545; }
                                .table-info, .table-summary { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                                .table-info td { padding: 8px 12px; border-bottom: 1px solid #edf2f7; font-size: 14px; }
                                .table-info td.label { font-weight: 600; color: #4a5568; width: 35%; }
                                .table-summary th, .table-summary td { padding: 10px; text-align: center; border: 1px solid #e2e8f0; font-size: 14px; }
                                .table-summary th { background-color: #f7fafc; color: #4a5568; font-weight: 600; }
                                .stat-pass { color: #28a745; font-weight: bold; }
                                .stat-fail { color: #dc3545; font-weight: bold; }
                                .stat-skip { color: #ffc107; font-weight: bold; }
                                .box { background-color: #fff5f5; border-left: 4px solid #dc3545; padding: 14px 18px; border-radius: 4px; margin-bottom: 20px; }
                                .box h4 { margin: 0 0 8px 0; color: #b71c1c; font-size: 15px; }
                                .box ul { margin: 0; padding-left: 20px; font-size: 13px; color: #555; }
                                .btn-container { text-align: center; margin: 25px 0 10px 0; }
                                .btn { background-color: #dc3545; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block; }
                                .footer { background: #fafafa; padding: 16px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #edf2f7; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>${env.PROJECT_NAME}</h1>
                                    <p>Automated Test Execution Failure Notification</p>
                                </div>
                                <div class="content">
                                    <div class="status-banner">
                                        BUILD FAILED
                                    </div>
                                    <table class="table-info">
                                        <tr>
                                            <td class="label">Job Name:</td>
                                            <td>${env.JOB_NAME}</td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build Number:</td>
                                            <td>#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build Status:</td>
                                            <td><strong style="color: #dc3545;">FAILURE</strong></td>
                                        </tr>
                                        <tr>
                                            <td class="label">Git Commit:</td>
                                            <td><code>${env.GIT_COMMIT ?: 'Latest master'}</code></td>
                                        </tr>
                                        <tr>
                                            <td class="label">Build URL:</td>
                                            <td><a href="${env.BUILD_URL}" style="color: #0d6efd;">${env.BUILD_URL}</a></td>
                                        </tr>
                                        <tr>
                                            <td class="label">HTML Report:</td>
                                            <td><a href="${env.BUILD_URL}HTML_20Automation_20Report/" style="color: #0d6efd;">View HTML Report</a></td>
                                        </tr>
                                    </table>

                                    <h3 style="color: #2d3748; font-size: 16px; margin-bottom: 10px;">Test Report Summary</h3>
                                    <table class="table-summary">
                                        <thead>
                                            <tr>
                                                <th>Total Tests</th>
                                                <th>Passed</th>
                                                <th>Failed</th>
                                                <th>Skipped</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td><strong>\${TEST_COUNTS, var="total"}</strong></td>
                                                <td class="stat-pass">\${TEST_COUNTS, var="pass"}</td>
                                                <td class="stat-fail">\${TEST_COUNTS, var="fail"}</td>
                                                <td class="stat-skip">\${TEST_COUNTS, var="skip"}</td>
                                            </tr>
                                        </tbody>
                                    </table>

                                    <div class="box">
                                        <h4>Attached Artifacts & Logs:</h4>
                                        <ul>
                                            <li><strong>Build Console Log:</strong> Attached to this email</li>
                                            <li><strong>HTML Report:</strong> <code>report.html</code></li>
                                            <li><strong>Excel Execution Report:</strong> <code>Test-Execution-Report.xlsx</code></li>
                                            <li><strong>JUnit XML Results:</strong> <code>results.xml</code></li>
                                        </ul>
                                    </div>

                                    <div class="btn-container">
                                        <a href="${env.BUILD_URL}console" class="btn">View Console Output</a>
                                    </div>
                                </div>
                                <div class="footer">
                                    This email was automatically generated by Jenkins CI/CD.
                                </div>
                            </div>
                        </body>
                        </html>
                        """,
                        mimeType: 'text/html',
                        attachmentsPattern: 'reports/*.html, reports/*.xlsx, reports/*.xml',
                        attachLog: true
                    )
                } catch (Exception e) {
                    echo "[WARNING] Failure email notification failed: ${e.message}"
                }
            }
        }
    }
}
