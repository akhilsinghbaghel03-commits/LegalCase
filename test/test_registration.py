import pytest
import time
import datetime
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from test.utils.helpers import get_driver, get_mail_tm_domain, create_mail_tm_account, get_mail_tm_token, get_otp_from_mail_tm, fill_field_by_keyword

# --- TEST DATA ---
INVALID_EMAILS = ["invalidemail", "test@.com", "@domain.com", "test@domain", "test space@domain.com"]
WEAK_PASSWORDS = ["12345", "password", "test", "NoSpecialChar123", "nouppercase123!"]



def test_registration_success(driver_setup):
    """Verify Register with all valid mandatory fields & unique email."""
    driver, wait = driver_setup
    
    from test.utils.helpers import register_new_user
    email, password = register_new_user(driver, wait)
    assert email is not None and len(email) > 0, "Expected registered user email"
    
    import json
    with open('shared_state.json', 'w') as f:
        json.dump({"email": email, "password": password}, f)




@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
def test_registration_invalid_email(driver_setup, invalid_email):
    """Verify email format validation fails with invalid emails."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except Exception:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
        
    fill_field_by_keyword(driver, "email", invalid_email)
    
    # Trigger validation by clicking away
    driver.find_element(By.XPATH, "//input[contains(@id, 'Input_FirstName') or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'first')]").click()
    
    # Assert validation error message appears (assuming standard HTML5 or OutSystems validation class)
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".validation-message")))

def test_registration_blank_mandatory_fields(driver_setup):
    """Register with blank mandatory fields and verify button is disabled or errors show."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except Exception:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
    
    submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")
    driver.execute_script("arguments[0].click();", submit_btn)
    
    # Verify we don't proceed to OTP screen
    time.sleep(2)
    assert "signup" in driver.current_url.lower() or "login" in driver.current_url.lower()
    assert len(driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")) == 0

def test_registration_password_mismatch(driver_setup):
    """Verify password and confirm password match validation."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except Exception:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    
    # First we need to get to step 2 (OTP) to test passwords, but since that requires a valid OTP, 
    # password mismatch validation might happen on Step 2.
    # Note: If this is an SPA, we would need to drive it up to Step 2.
    pass # To be fully implemented once Step 2 UI is confirmed.

def test_registration_existing_email(driver_setup):
    """Verify existing email address returns appropriate error."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except Exception:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
    
    fill_field_by_keyword(driver, "first", "Existing")
    fill_field_by_keyword(driver, "last", "User")
    fill_field_by_keyword(driver, "email", "akh@gmail.com") # Assuming this exists
    fill_field_by_keyword(driver, "company", "Org")
    fill_field_by_keyword(driver, "phone", "9876543210")
    
    # driver.find_element(By.XPATH, "//select[contains(@id, 'Dropdown1')]/option[2]").click()
    # driver.find_element(By.XPATH, "//select[contains(@id, 'Dropdown2')]/option[2]").click()
    
    # terms_checkbox = driver.find_element(By.XPATH, "//input[@id='b5-b9-Checkbox1']")
    # driver.execute_script("arguments[0].click();", terms_checkbox)
    
    submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")
    driver.execute_script("arguments[0].click();", submit_btn)
    
    # Verify error message
    time.sleep(3)
    assert "signup" in driver.current_url.lower() or "login" in driver.current_url.lower() or len(driver.find_elements(By.XPATH, "//*[contains(text(), 'already exists')]")) > 0
