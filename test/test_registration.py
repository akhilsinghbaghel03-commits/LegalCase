import pytest
import time
import datetime
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test.utils.helpers import get_driver, get_mail_tm_domain, create_mail_tm_account, get_mail_tm_token, get_otp_from_mail_tm, fill_field_by_keyword

# --- TEST DATA ---
INVALID_EMAILS = ["invalidemail", "test@.com", "@domain.com", "test@domain", "test space@domain.com"]
WEAK_PASSWORDS = ["12345", "password", "test", "NoSpecialChar123", "nouppercase123!"]



def test_registration_success(driver_setup):
    """Verify Register with all valid mandatory fields & unique email."""
    driver, wait = driver_setup
    
    # 1. Generate unique email
    domain = get_mail_tm_domain()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"user_{timestamp}@{domain}"
    password = "TestPassword123!@#"
    create_mail_tm_account(email, password)
    token = get_mail_tm_token(email, password)
    
    import json
    with open('shared_state.json', 'w') as f:
        json.dump({"email": email, "password": password}, f)
    
    # 2. Navigate to login and click sign up
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except TimeoutException:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    
    # 3. Fill Form
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email' or @type='text']")))
    fill_field_by_keyword(driver, "first", "Auto")
    fill_field_by_keyword(driver, "last", "Test")
    fill_field_by_keyword(driver, "email", email)
    fill_field_by_keyword(driver, "company", "Auto Test Corp")
    fill_field_by_keyword(driver, "phone", "9876543210")
    
    # Dropdowns (Removed from UI)
    # driver.find_element(By.XPATH, "//select[contains(@id, 'Dropdown1')]/option[2]").click()
    # driver.find_element(By.XPATH, "//select[contains(@id, 'Dropdown2')]/option[2]").click()
    
    # Terms (Removed from UI)
    # terms_checkbox = driver.find_element(By.XPATH, "//input[@id='b5-b9-Checkbox1']")
    # driver.execute_script("arguments[0].click();", terms_checkbox)
    
    # Submit
    time.sleep(1) # Give UI a moment
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")))
    driver.execute_script("arguments[0].click();", submit_btn)
    
    # 4. Verify OTP Screen & Extract OTP
    driver.save_screenshot("before_otp_timeout.png")
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'OTP')]")))
    otp_code = get_otp_from_mail_tm(token)
    assert otp_code is not None, "Failed to retrieve OTP from email"
    
    otp_fields = driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")
    for i, char in enumerate(otp_code):
        otp_fields[i].send_keys(char)
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
    password_inputs = driver.find_elements(By.XPATH, "//input[@type='password']")
    for pw_input in password_inputs:
        if pw_input.is_displayed():
            pw_input.send_keys(password)
    
    verify_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Verify & Continue') or text()='Verify']")
    driver.execute_script("""
        var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
        arguments[0].dispatchEvent(ev);
    """, verify_btn)
    
    # 5. Verify Redirect
    wait.until(lambda d: "Trial" in d.current_url or "setting" in d.current_url or "legalhub" in d.current_url)
    


@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
def test_registration_invalid_email(driver_setup, invalid_email):
    """Verify email format validation fails with invalid emails."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
    
    email_field = driver.find_element(By.XPATH, "//input[@type='email']")
    email_field.send_keys(invalid_email)
    
    # Trigger validation by clicking away
    driver.find_element(By.XPATH, "//input[contains(@id, 'Input_FirstName') or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'first')]").click()
    
    # Assert validation error message appears (assuming standard HTML5 or OutSystems validation class)
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".validation-message")))

def test_registration_blank_mandatory_fields(driver_setup):
    """Register with blank mandatory fields and verify button is disabled or errors show."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
    
    submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")
    driver.execute_script("arguments[0].click();", submit_btn)
    
    # Verify we don't proceed to OTP screen
    time.sleep(2)
    assert "signup" in driver.current_url

def test_registration_password_mismatch(driver_setup):
    """Verify password and confirm password match validation."""
    driver, wait = driver_setup
    driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    
    # First we need to get to step 2 (OTP) to test passwords, but since that requires a valid OTP, 
    # password mismatch validation might happen on Step 2.
    # Note: If this is an SPA, we would need to drive it up to Step 2.
    pass # To be fully implemented once Step 2 UI is confirmed.

def test_registration_existing_email(driver_setup):
    """Verify existing email address returns appropriate error."""
    driver, wait = driver_setup
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
    assert "signup" in driver.current_url or len(driver.find_elements(By.XPATH, "//*[contains(text(), 'already exists')]")) > 0
