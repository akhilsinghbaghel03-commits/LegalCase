pipeline {
    agent any

    options {
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    environment {
        PROJECT_NAME    = 'YorPro Automation'
        RECIPIENT_EMAIL = 'akhil.singh@yorpro.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                bat """
                    @echo off
                    if not exist "reports" mkdir "reports"
                    if not exist ".venv" (
                        python -m venv .venv
                    )
                    call .venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Execute Automation Tests') {
            steps {
                bat """
                    @echo off
                    call .venv\\Scripts\\activate.bat
                    echo ========================================
                    echo Executing Selenium Pytest Suite
                    echo ========================================
                    python -m pytest test/ --junitxml=reports/results.xml --html=reports/report.html --self-contained-html -v
                """
            }
        }

        stage('Generate Excel Report') {
            steps {
                bat """
                    @echo off
                    call .venv\\Scripts\\activate.bat
                    echo ========================================
                    echo Generating Excel Test Execution Report
                    echo ========================================
                    python generate_excel_report.py
                """
            }
        }
    }

    post {
        always {
            script {
                // 1. Process JUnit XML results for test metrics
                junit testResults: 'reports/results.xml', allowEmptyResults: true

                // 2. Archive all report artifacts
                archiveArtifacts artifacts: 'reports/**, *.html, *.xlsx, *.png, *.mp4', allowEmptyArchive: true

                // 3. Publish HTML Report if HTML Publisher plugin is installed
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'HTML Automation Report'
                ])

                // 4. Capture Test Metrics dynamically
                def totalTests   = currentBuild.totalTestCount ?: 0
                def failedTests  = currentBuild.failCount ?: 0
                def skippedTests = currentBuild.skipCount ?: 0
                def passedTests  = (totalTests - failedTests - skippedTests) >= 0 ? (totalTests - failedTests - skippedTests) : 0
                def buildStatus  = currentBuild.currentResult ?: 'UNKNOWN'
                def execTime     = new Date().format("yyyy-MM-dd HH:mm:ss", TimeZone.getTimeZone('UTC')) + ' UTC'

                // Status Badge Color
                def statusColor = (buildStatus == 'SUCCESS') ? '#28a745' : (buildStatus == 'UNSTABLE' ? '#ffc107' : '#dc3545')

                // Email Subject
                def emailSubject = "Automation ${buildStatus} - ${env.JOB_NAME} #${env.BUILD_NUMBER}"

                // Email HTML Body
                def emailBody = """
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
                        .container { max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e1e4e8; }
                        .header { background: #1a237e; color: #ffffff; padding: 24px; text-align: center; }
                        .header h1 { margin: 0; font-size: 22px; font-weight: 600; letter-spacing: 0.5px; }
                        .header p { margin: 6px 0 0 0; font-size: 14px; opacity: 0.85; }
                        .content { padding: 24px; }
                        .status-banner { text-align: center; padding: 12px; margin-bottom: 20px; border-radius: 6px; font-size: 18px; font-weight: bold; color: #ffffff; background-color: ${statusColor}; }
                        .table-info, .table-summary { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                        .table-info td { padding: 8px 12px; border-bottom: 1px solid #edf2f7; font-size: 14px; }
                        .table-info td.label { font-weight: 600; color: #4a5568; width: 35%; }
                        .table-summary th, .table-summary td { padding: 10px; text-align: center; border: 1px solid #e2e8f0; font-size: 14px; }
                        .table-summary th { background-color: #f7fafc; color: #4a5568; font-weight: 600; }
                        .stat-pass { color: #28a745; font-weight: bold; }
                        .stat-fail { color: #dc3545; font-weight: bold; }
                        .stat-skip { color: #ffc107; font-weight: bold; }
                        .attachments-box { background-color: #f8f9fa; border-left: 4px solid #1a237e; padding: 14px 18px; border-radius: 4px; margin-bottom: 20px; }
                        .attachments-box h4 { margin: 0 0 8px 0; color: #1a237e; font-size: 15px; }
                        .attachments-box ul { margin: 0; padding-left: 20px; font-size: 13px; color: #555; }
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
                                BUILD ${buildStatus}
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
                                    <td class="label">Execution Time:</td>
                                    <td>${execTime}</td>
                                </tr>
                                <tr>
                                    <td class="label">Triggered URL:</td>
                                    <td><a href="${env.BUILD_URL}" style="color: #0d6efd;">${env.BUILD_URL}</a></td>
                                </tr>
                            </table>

                            <h3 style="color: #2d3748; font-size: 16px; margin-bottom: 10px;">Test Execution Metrics</h3>
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
                                        <td><strong>${totalTests}</strong></td>
                                        <td class="stat-pass">${passedTests}</td>
                                        <td class="stat-fail">${failedTests}</td>
                                        <td class="stat-skip">${skippedTests}</td>
                                    </tr>
                                </tbody>
                            </table>

                            <div class="attachments-box">
                                <h4>Attached Reports & Artifacts:</h4>
                                <ul>
                                    <li><strong>HTML Automation Report:</strong> <code>report.html</code></li>
                                    <li><strong>Excel Test Execution Report:</strong> <code>Test-Execution-Report.xlsx</code></li>
                                    <li><strong>JUnit Test XML Results:</strong> <code>results.xml</code></li>
                                </ul>
                            </div>

                            <div class="btn-container">
                                <a href="${env.BUILD_URL}console" class="btn">View Jenkins Console Log</a>
                            </div>
                        </div>
                        <div class="footer">
                            This is an automated message generated by Jenkins Pipeline for ${env.PROJECT_NAME}.
                        </div>
                    </div>
                </body>
                </html>
                """

                // 5. Send Email via Email Extension Plugin (emailext)
                emailext (
                    to: env.RECIPIENT_EMAIL,
                    subject: emailSubject,
                    body: emailBody,
                    mimeType: 'text/html',
                    attachmentsPattern: 'reports/*.html, reports/*.xlsx, reports/*.xml',
                    attachLog: (buildStatus != 'SUCCESS')
                )
            }
        }
    }
}
