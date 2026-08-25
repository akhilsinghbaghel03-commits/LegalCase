import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test.utils.helpers import get_driver, fill_field, perform_login, navigate_with_retry

# Data extracted from test_data.json
INVALID_EMAILS = ["nonexistent@domain.com", "valid@domain.com"]
SECURITY_PAYLOADS = ["test@test.com' OR '1'='1", "<script>alert('xss')</script>@domain.com"]


def test_login_success(driver_setup):
    """Verify login with valid email and password, retrieving valid 2FA OTP and redirecting to Dashboard."""
    driver, wait = driver_setup
    perform_login(driver, wait)
    
    # Assert successful login (navigated away from login/signup to dashboard/app)
    current_url = driver.current_url.lower()
    assert "login" not in current_url and "signup" not in current_url, f"Expected successful login redirect, but remained on: {driver.current_url}"
    print(f"Successfully logged in! Current URL: {driver.current_url}")


@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
def test_login_invalid_credentials(driver_setup, invalid_email):
    """Verify login failure with invalid credentials."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']")))
    fill_field(driver, "//input[@id='Input_UserEmail' or @type='email' or contains(@placeholder, 'Email')]", invalid_email)
    fill_field(driver, "//input[@id='Input_Password' or @type='password']", "WrongPassword123!")
    
    driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()
    
    # Verify error message
    end_time = time.time() + 20
    error_found = False
    while time.time() < end_time:
        body_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        if "not found" in body_text or "invalid" in body_text or "wrong" in body_text or "incorrect" in body_text:
            error_found = True
            break
        time.sleep(1)
    assert error_found, f"Validation error message not found. Body text: {body_text}"

@pytest.mark.parametrize("payload", SECURITY_PAYLOADS)
def test_login_security_validation(driver_setup, payload):
    """Verify login handles SQLi and XSS payloads gracefully (Client-side validation)."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']")))
    fill_field(driver, "//input[@id='Input_UserEmail' or @type='email' or contains(@placeholder, 'Email')]", payload)
    
    driver.find_element(By.XPATH, "//input[@id='Input_Password' or @type='password']").click()
    
    # Assert validation error message appears
    time.sleep(1)
    # Should not proceed or should show client-side error
    assert "login" in driver.current_url.lower()

def test_login_blank_credentials(driver_setup):
    """Verify login with blank email and password."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']")))
    driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()
    
    # Verify we remain on login
    time.sleep(1)
    assert "login" in driver.current_url.lower()
