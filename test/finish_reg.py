import time
import datetime
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from test.utils.helpers import get_driver, fill_field_by_keyword, get_mail_tm_domain, create_mail_tm_account, get_mail_tm_token, get_otp_from_mail_tm

def run():
    driver, wait = get_driver()
    
    domain = get_mail_tm_domain()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"user_{timestamp}@{domain}"
    password = "TestPassword123!@#"
    create_mail_tm_account(email, password)
    token = get_mail_tm_token(email, password)
    
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    
    # Intercept fetch
    interceptor = """
    window.capturedResponses = [];
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const response = await originalFetch.apply(this, args);
        const clone = response.clone();
        if (args[0] && typeof args[0] === 'string' && args[0].includes('registration')) {
            clone.text().then(text => {
                window.capturedResponses.push(text);
            });
        }
        return response;
    };
    """
    driver.execute_script(interceptor)
    
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except:
        driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email' or @type='text']")))
    fill_field_by_keyword(driver, "first", "Auto")
    fill_field_by_keyword(driver, "last", "Test")
    fill_field_by_keyword(driver, "email", email)
    fill_field_by_keyword(driver, "company", "Auto Test Corp")
    fill_field_by_keyword(driver, "phone", "9876543210")
    
    time.sleep(2)
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")))
    try:
        submit_btn.click()
    except:
        driver.execute_script("arguments[0].click();", submit_btn)
    
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'OTP')]")))
    otp_code = get_otp_from_mail_tm(token)
    
    otp_fields = driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")
    for i, char in enumerate(otp_code):
        otp_fields[i].send_keys(char)
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
    password_inputs = driver.find_elements(By.XPATH, "//input[@type='password']")
    for pw_input in password_inputs:
        if pw_input.is_displayed():
            try:
                pw_input.click()
                time.sleep(0.1)
                pw_input.send_keys(password)
                time.sleep(0.1)
                pw_input.send_keys(Keys.TAB)
            except:
                pass
            
    time.sleep(1)
    
    driver.execute_script("console.clear();")
    
    verify_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Verify & Continue') or text()='Verify']")
    verify_btn.click()
    
    time.sleep(5)
    
    # Check for error popup text
    try:
        err_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'Something went wrong') or contains(@class, 'feedback-message-error')]").text
        print(f"UI ERROR MESSAGE: {err_msg}")
    except:
        pass
    
    # Check captured responses
    responses = driver.execute_script("return window.capturedResponses;")
    print(f"CAPTURED RESPONSES: {responses}")
    
    driver.quit()

if __name__ == "__main__":
    run()
