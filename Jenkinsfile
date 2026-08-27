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
        PROJECT_NAME    = 'YorPro'
        ENVIRONMENT     = 'DEV'
        BROWSER         = 'Chrome'
        RECIPIENT_TO    = 'akhilsinghbaghel03@gmail.com'
        RECIPIENT_CC    = ''
        RECIPIENT_BCC   = ''
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

                    // Execute pytest and capture return code safely to ensure reports and email always execute
                    env.PYTEST_EXIT_CODE = bat(
                        script: """
                            @echo off
                            "${PYTHON_EXE}" -m pytest --junitxml=reports/results.xml --html=reports/report.html --self-contained-html -v
                        """,
                        returnStatus: true
                    ).toString()

                    echo "Pytest execution finished with exit code: ${env.PYTEST_EXIT_CODE}"
                }
            }
        }

        stage('Generate Professional Reports') {
            steps {
                script {
                    echo "==============================================================================="
                    echo "[STEP 6] Generating Advanced Excel and HTML Reports"
                    echo "==============================================================================="

                    def scriptExists = fileExists 'generate_excel_report.py'
                    if (!scriptExists) {
                        echo "[ERROR] generate_excel_report.py was not found in the workspace!"
                    } else {
                        def reportStatus = bat(
                            script: """
                                @echo off
                                set PROJECT_NAME=${env.PROJECT_NAME}
                                set ENVIRONMENT=${env.ENVIRONMENT}
                                set BUILD_NUMBER=${env.BUILD_NUMBER}
                                set BUILD_URL=${env.BUILD_URL}
                                set JOB_NAME=${env.JOB_NAME}
                                set BROWSER=${env.BROWSER}
                                "${PYTHON_EXE}" generate_excel_report.py
                            """,
                            returnStatus: true
                        )

                        if (reportStatus != 0) {
                            echo "[WARNING] Report generation script encountered an issue (Exit Code: ${reportStatus})."
                        } else {
                            echo "[SUCCESS] Excel, HTML, and Email Body reports generated successfully."
                        }
                    }

                    // Mark build status accurately based on pytest exit code
                    if (env.PYTEST_EXIT_CODE != "0") {
                        echo "[INFO] Pytest reported failure(s). Marking build status as FAILURE."
                        currentBuild.result = 'FAILURE'
                    } else {
                        echo "[INFO] All test cases executed successfully without failures."
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                script {
                    echo "==============================================================================="
                    echo "[STEP 7] Publishing Test Reports & Archiving Artifacts"
                    echo "==============================================================================="

                    // 1. Publish JUnit XML Test Results
                    junit testResults: 'reports/results.xml', allowEmptyResults: true

                    // 2. Publish HTML Report
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'HTML Automation Report'
                    ])

                    // 3. Archive all generated reports and artifacts
                    archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            script {
                echo "==============================================================================="
                echo "[STEP 8] Verifying Attachments & Sending Email Notification"
                echo "==============================================================================="

                def buildStatus = currentBuild.currentResult ?: (env.PYTEST_EXIT_CODE == "0" ? "SUCCESS" : "FAILURE")
                def safeProj = env.PROJECT_NAME.replaceAll("[^a-zA-Z0-9_]+", "_")
                def safeEnv  = env.ENVIRONMENT.replaceAll("[^a-zA-Z0-9_]+", "_")
                def excelName = "${safeProj}_${safeEnv}_Automation_Report_Build_${env.BUILD_NUMBER}.xlsx"
                def htmlName  = "${safeProj}_${safeEnv}_Automation_Report_Build_${env.BUILD_NUMBER}.html"

                def excelPath = "reports/${excelName}"
                def htmlPath  = "reports/${htmlName}"

                // Check canonical fallback names if dynamic names are not present
                if (!fileExists(excelPath)) {
                    excelPath = "reports/Test-Execution-Report.xlsx"
                }
                if (!fileExists(htmlPath)) {
                    htmlPath = "reports/report.html"
                }

                // 1. Verify attachments exist and are non-empty
                def excelExists = fileExists(excelPath)
                def htmlExists  = fileExists(htmlPath)
                def attachmentCount = 0

                if (excelExists) {
                    echo "Excel Report: ${excelPath}"
                    attachmentCount++
                } else {
                    echo "[ERROR] Missing attachment: Excel report not found at ${excelPath}!"
                }

                if (htmlExists) {
                    echo "HTML Report: ${htmlPath}"
                    attachmentCount++
                } else {
                    echo "[ERROR] Missing attachment: HTML report not found at ${htmlPath}!"
                }

                echo "Email Attachments: ${attachmentCount}"

                // 2. Load email body HTML or fall back to structured inline template
                def emailBody = ""
                def emailFile = "reports/email_notification.html"
                if (fileExists(emailFile)) {
                    try {
                        emailBody = readFile(file: emailFile, encoding: 'UTF-8')
                    } catch (Exception e) {
                        echo "[WARNING] Could not read email_notification.html: ${e.message}. Using built-in template."
                    }
                }

                if (!emailBody || emailBody.trim().isEmpty()) {
                    def statusColor = (buildStatus == 'SUCCESS') ? '#28a745' : '#dc3545'
                    def failureSection = ""
                    if (buildStatus == 'SUCCESS') {
                        failureSection = """
                        <h3 style="color: #2d3748; margin-top: 25px; margin-bottom: 10px; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Failed Test Cases</h3>
                        <p style="margin: 12px 0 20px 0; color: #28a745; font-weight: bold; background-color: #f0fff4; border: 1px solid #c6f6d5; padding: 12px 16px; border-radius: 6px;">
                            No test cases failed during this execution.
                        </p>
                        """
                    } else {
                        failureSection = """
                        <h3 style="color: #742a2a; margin-top: 25px; margin-bottom: 10px; font-size: 16px; border-bottom: 2px solid #feb2b2; padding-bottom: 6px;">Failed Test Cases</h3>
                        <p style="margin: 12px 0 20px 0; color: #dc3545; font-weight: bold; background-color: #fff5f5; border: 1px solid #feb2b2; padding: 12px 16px; border-radius: 6px;">
                            Test failure(s) detected during execution. Please inspect attached reports for complete stack traces and details.
                        </p>
                        """
                    }

                    emailBody = """
                    <!DOCTYPE html>
                    <html>
                    <head><meta charset="utf-8"></head>
                    <body style="font-family: 'Segoe UI', Arial, Helvetica, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333333; line-height: 1.5;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="680" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e4e8;">
                            <tr>
                                <td style="background-color: #1a365d; padding: 24px 30px; color: #ffffff; text-align: center;">
                                    <h1 style="margin: 0; font-size: 22px; font-weight: 700;">[Automation Test Report] ${env.PROJECT_NAME}</h1>
                                    <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">Environment: <strong>${env.ENVIRONMENT}</strong> &bull; Build <strong>#${env.BUILD_NUMBER}</strong></p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 28px 32px;">
                                    <p style="font-size: 15px; margin: 0 0 10px 0;"><strong>Hello Team,</strong></p>
                                    <p style="font-size: 14px; color: #4a5568; margin: 0 0 20px 0;">The automation test execution has been completed. Please find the execution summary below.</p>

                                    <h3 style="color: #1a365d; margin: 0 0 10px 0; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Execution Summary</h3>
                                    <table width="100%" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin-bottom: 24px; font-size: 14px;">
                                        <tr style="background-color: #f7fafc;">
                                            <th width="35%" style="text-align: left; padding: 10px 12px; border: 1px solid #e2e8f0; color: #4a5568;">Field</th>
                                            <th width="65%" style="text-align: left; padding: 10px 12px; border: 1px solid #e2e8f0; color: #4a5568;">Details</th>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Project</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;">${env.PROJECT_NAME}</td>
                                        </tr>
                                        <tr style="background-color: #fcfdfe;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Environment</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;">${env.ENVIRONMENT}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Build Number</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;">#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr style="background-color: #fcfdfe;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Execution Status</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;"><strong style="color: ${statusColor}; font-size: 14px;">${buildStatus}</strong></td>
                                        </tr>
                                    </table>

                                    <h3 style="color: #1a365d; margin: 0 0 10px 0; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Test Summary</h3>
                                    <table width="100%" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin-bottom: 24px; font-size: 14px;">
                                        <tr style="background-color: #f7fafc;">
                                            <th width="65%" style="text-align: left; padding: 10px 12px; border: 1px solid #e2e8f0; color: #4a5568;">Metric</th>
                                            <th width="35%" style="text-align: right; padding: 10px 12px; border: 1px solid #e2e8f0; color: #4a5568;">Count</th>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600;">Total Test Cases</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; text-align: right; font-weight: bold;">\${TEST_COUNTS, var="total"}</td>
                                        </tr>
                                        <tr style="background-color: #f0fff4;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #22543d;">Passed</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; text-align: right; font-weight: bold; color: #28a745;">\${TEST_COUNTS, var="pass"}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600;">Failed</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; text-align: right; font-weight: bold; color: #dc3545;">\${TEST_COUNTS, var="fail"}</td>
                                        </tr>
                                        <tr style="background-color: #fefcbf;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #744210;">Skipped</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; text-align: right; font-weight: bold; color: #d69e2e;">\${TEST_COUNTS, var="skip"}</td>
                                        </tr>
                                    </table>

                                    ${failureSection}

                                    <h3 style="color: #1a365d; margin: 0 0 10px 0; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">Jenkins Build Information</h3>
                                    <table width="100%" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin-bottom: 20px; font-size: 14px;">
                                        <tr>
                                            <td width="35%" style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Build Number</td>
                                            <td width="65%" style="padding: 8px 12px; border: 1px solid #e2e8f0;">#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr style="background-color: #fcfdfe;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Build Status</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;"><strong style="color: ${statusColor};">${buildStatus}</strong></td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Jenkins Job Name</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;">${env.JOB_NAME}</td>
                                        </tr>
                                        <tr style="background-color: #fcfdfe;">
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0; font-weight: 600; color: #4a5568;">Jenkins Build URL</td>
                                            <td style="padding: 8px 12px; border: 1px solid #e2e8f0;"><a href="${env.BUILD_URL}" style="color: #3182ce; text-decoration: none;">${env.BUILD_URL}</a></td>
                                        </tr>
                                    </table>

                                    <div style="text-align: center; margin: 25px 0 10px 0;">
                                        <a href="${env.BUILD_URL}" style="background-color: #3182ce; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block;">View Jenkins Build</a>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #fafafa; padding: 20px 32px; border-top: 1px solid #edf2f7; font-size: 13px; color: #4a5568;">
                                    <p style="margin: 0 0 4px 0;"><strong>Regards,</strong></p>
                                    <p style="margin: 0 0 12px 0; font-weight: 600; color: #1a365d;">Automation Testing Team</p>
                                    <p style="margin: 0; font-size: 12px; color: #a0aec0; font-style: italic;">This is an automated email generated by the Jenkins automation pipeline. Please do not reply directly to this email.</p>
                                </td>
                            </tr>
                        </table>
                    </body>
                    </html>
                    """
                }

                // 3. Send email via emailext with verified attachments
                def recipientTo  = env.RECIPIENT_TO ?: 'akhilsinghbaghel03@gmail.com'
                def recipientCc  = env.RECIPIENT_CC ?: ''
                def recipientBcc = env.RECIPIENT_BCC ?: ''
                def emailSubject = "[Automation Test Report] ${env.PROJECT_NAME} | ${env.ENVIRONMENT} | Build #${env.BUILD_NUMBER} | ${buildStatus}"

                try {
                    emailext (
                        to: recipientTo,
                        cc: recipientCc,
                        bcc: recipientBcc,
                        subject: emailSubject,
                        body: emailBody,
                        mimeType: 'text/html',
                        attachmentsPattern: 'reports/*.xlsx, reports/*.html, reports/*.xml',
                        attachLog: (buildStatus != 'SUCCESS')
                    )
                    echo "Email sent successfully."
                } catch (Exception e) {
                    echo "[WARNING] Email notification delivery failed: ${e.message}"
                }
            }
        }
    }
}
