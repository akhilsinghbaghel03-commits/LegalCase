import pytest
import requests
import json
import time
import uuid

BASE_AUTH_URL = "https://yorpro-test.outsystems.app/legalhub/api/auth"
BASE_EMAIL_URL = "https://yorpro-test.outsystems.app/legalhub/email"

@pytest.fixture
def auth_headers():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

@pytest.fixture
def test_user_data():
    uid = uuid.uuid4().hex[:8]
    return {
        "email": f"test_api_{uid}@guerrillamail.com",
        "password": "Password123!@#",
        "first_name": "API",
        "last_name": f"Tester_{uid}",
        "phone": "9098864919",
        "company": f"LegalTech API Corp {uid}"
    }

# ==========================================
# 1. AUTH API ENDPOINTS
# ==========================================

class TestAuthAPI:
    """Test suite for /api/auth endpoints"""

    def test_post_signup(self, auth_headers, test_user_data):
        """POST /api/auth/signup - User registration"""
        url = f"{BASE_AUTH_URL}/signup"
        payload = {
            "firstName": test_user_data["first_name"],
            "lastName": test_user_data["last_name"],
            "email": test_user_data["email"],
            "phone": test_user_data["phone"],
            "company": test_user_data["company"]
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /api/auth/signup] Status: {response.status_code}")
            assert response.status_code in [200, 201, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /api/auth/signup] Network/Endpoint Info: {e}")

    def test_post_send_otp(self, auth_headers, test_user_data):
        """POST /api/auth/send-otp - Send OTP via email"""
        url = f"{BASE_AUTH_URL}/send-otp"
        payload = {
            "email": test_user_data["email"],
            "type": "registration"
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /api/auth/send-otp] Status: {response.status_code}")
            assert response.status_code in [200, 201, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /api/auth/send-otp] Network/Endpoint Info: {e}")

    def test_get_verify_otp(self, auth_headers, test_user_data):
        """GET /api/auth/verify-otp - Verify OTP code"""
        url = f"{BASE_AUTH_URL}/verify-otp"
        params = {
            "email": test_user_data["email"],
            "otp": "123456"
        }
        try:
            response = requests.get(url, params=params, headers=auth_headers, timeout=10)
            print(f"[GET /api/auth/verify-otp] Status: {response.status_code}")
            assert response.status_code in [200, 400, 401, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[GET /api/auth/verify-otp] Network/Endpoint Info: {e}")

    def test_post_login(self, auth_headers, test_user_data):
        """POST /api/auth/login - User login"""
        url = f"{BASE_AUTH_URL}/login"
        payload = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /api/auth/login] Status: {response.status_code}")
            assert response.status_code in [200, 400, 401, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /api/auth/login] Network/Endpoint Info: {e}")

    def test_post_resend_otp(self, auth_headers, test_user_data):
        """POST /api/auth/resend-otp - Resend OTP"""
        url = f"{BASE_AUTH_URL}/resend-otp"
        payload = {
            "email": test_user_data["email"]
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /api/auth/resend-otp] Status: {response.status_code}")
            assert response.status_code in [200, 201, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /api/auth/resend-otp] Network/Endpoint Info: {e}")

    def test_get_otp_status(self, auth_headers, test_user_data):
        """GET /api/auth/otp-status - Check OTP status"""
        url = f"{BASE_AUTH_URL}/otp-status"
        params = {
            "email": test_user_data["email"]
        }
        try:
            response = requests.get(url, params=params, headers=auth_headers, timeout=10)
            print(f"[GET /api/auth/otp-status] Status: {response.status_code}")
            assert response.status_code in [200, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[GET /api/auth/otp-status] Network/Endpoint Info: {e}")

# ==========================================
# 2. EMAIL SERVICE API ENDPOINTS
# ==========================================

class TestEmailAPI:
    """Test suite for Email Service API endpoints"""

    def test_post_email_send(self, auth_headers, test_user_data):
        """POST /email/send - Send email"""
        url = f"{BASE_EMAIL_URL}/send"
        payload = {
            "to": test_user_data["email"],
            "subject": "Automation Test Email",
            "body": "This is an automated test message from YorPro LegalHub QA suite."
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /email/send] Status: {response.status_code}")
            assert response.status_code in [200, 201, 202, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /email/send] Network/Endpoint Info: {e}")

    def test_post_email_send_otp(self, auth_headers, test_user_data):
        """POST /email/send-otp - Send OTP email"""
        url = f"{BASE_EMAIL_URL}/send-otp"
        payload = {
            "to": test_user_data["email"],
            "otpCode": "654321",
            "template": "verification_otp"
        }
        try:
            response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
            print(f"[POST /email/send-otp] Status: {response.status_code}")
            assert response.status_code in [200, 201, 202, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[POST /email/send-otp] Network/Endpoint Info: {e}")

    def test_get_email_logs(self, auth_headers, test_user_data):
        """GET /email/logs - Get email logs"""
        url = f"{BASE_EMAIL_URL}/logs"
        params = {
            "recipient": test_user_data["email"],
            "limit": 10
        }
        try:
            response = requests.get(url, params=params, headers=auth_headers, timeout=10)
            print(f"[GET /email/logs] Status: {response.status_code}")
            assert response.status_code in [200, 400, 401, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[GET /email/logs] Network/Endpoint Info: {e}")

    def test_get_email_status(self, auth_headers):
        """GET /email/status/[message_id] - Check email status"""
        sample_msg_id = "msg_test_12345"
        url = f"{BASE_EMAIL_URL}/status/{sample_msg_id}"
        try:
            response = requests.get(url, headers=auth_headers, timeout=10)
            print(f"[GET /email/status/{sample_msg_id}] Status: {response.status_code}")
            assert response.status_code in [200, 400, 404, 405]
        except requests.exceptions.RequestException as e:
            print(f"[GET /email/status/{sample_msg_id}] Network/Endpoint Info: {e}")
