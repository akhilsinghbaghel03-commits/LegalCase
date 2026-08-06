import json
import time
import datetime
import random
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# API Constants
API_BASE_URL = "https://yorpro-test.outsystems.app"
API_ENDPOINT = f"{API_BASE_URL}/legalhub/api/auth/signup"  # Adjust exact endpoint as necessary

def generate_random_email():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_digits = f"{random.randint(1000, 9999)}"
    # Using guerrilla mail domain as an example based on existing code
    domain = "guerrillamail.com"
    return f"user_{timestamp}_{random_digits}@{domain}"

import urllib.request
import urllib.error

def test_api_signup():
    """
    Template 3: API-Based Signup Test
    """
    email = generate_random_email()
    password = "SecurePass@123"
    
    payload = {
        "email": email,
        "firstName": "TestFirstName",
        "lastName": "TestLastName",
        "password": password,
        "confirmPassword": password,
        "phoneNumber": "9876543210",
        "acceptTerms": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    results = {
        "test_name": "API-Based Signup Test",
        "timestamp": datetime.datetime.now().isoformat(),
        "email_used": email,
        "response_code": None,
        "status": "failed",
        "errors": ""
    }

    print(f"Testing API Signup for {email}...")
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(API_ENDPOINT, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                results["response_code"] = response.getcode()
                response_text = response.read().decode("utf-8")
                
                if results["response_code"] in [200, 201]:
                    results["status"] = "passed"
                    results["confirmation"] = json.loads(response_text) if response_text else "Success"
        except urllib.error.HTTPError as e:
            results["response_code"] = e.code
            response_text = e.read().decode("utf-8") if hasattr(e, 'read') else str(e)
            if e.code == 400:
                results["errors"] = f"Bad Request: {response_text}"
            elif e.code == 409:
                results["errors"] = "Email already exists"
            else:
                results["errors"] = f"Unexpected status: {e.code} - {response_text}"
        except urllib.error.URLError as e:
            results["errors"] = str(e.reason)
            
    except Exception as e:
        results["errors"] = str(e)
        
    return results

def setup_driver(browser_name):
    if browser_name.lower() == 'chrome':
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")
        return webdriver.Chrome(options=options)
    elif browser_name.lower() == 'firefox':
        options = webdriver.FirefoxOptions()
        # options.add_argument("--headless")
        return webdriver.Firefox(options=options)
    elif browser_name.lower() == 'edge':
        options = webdriver.EdgeOptions()
        # options.add_argument("--headless=new")
        return webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

def test_cross_browser_signup():
    """
    Template 4: Cross-Browser Signup Test
    """
    browsers = ['chrome', 'firefox', 'edge']
    all_results = []
    
    for browser in browsers:
        email = generate_random_email()
        result = {
            "test_date_time": datetime.datetime.now().isoformat(),
            "browser": browser,
            "version": "latest",
            "email_used": email,
            "status": "failed",
            "screenshot_path": "",
            "errors": ""
        }
        
        print(f"\n--- Testing on {browser.upper()} ---")
        driver = None
        try:
            driver = setup_driver(browser)
            wait = WebDriverWait(driver, 15)
            
            # 1. Navigate to URL
            app_url = "https://yorpro-test.outsystems.app/legalhub/Login"
            driver.get(app_url)
            
            # 2. Click signup button
            try:
                signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
                driver.execute_script("arguments[0].click();", signup_link)
            except:
                driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
                
            # 3. Fill form with random email
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            
            # Fill common fields (using generic locators for example)
            first_name = driver.find_element(By.XPATH, "//input[contains(@id, 'FirstName') or contains(@placeholder, 'First')]")
            first_name.send_keys("CrossBrowser")
            
            last_name = driver.find_element(By.XPATH, "//input[contains(@id, 'LastName') or contains(@placeholder, 'Last')]")
            last_name.send_keys("Test")
            
            email_field = driver.find_element(By.XPATH, "//input[@type='email']")
            email_field.send_keys(email)
            
            try:
                phone = driver.find_element(By.XPATH, "//input[@type='tel' or contains(@id, 'Phone')]")
                phone.send_keys("9876543210")
            except: pass
            
            try:
                company = driver.find_element(By.XPATH, "//input[contains(@id, 'Company')]")
                company.send_keys(f"Test Corp {browser}")
            except: pass
            
            # Submit
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next') or contains(., 'Sign Up')]")))
            driver.execute_script("arguments[0].click();", submit_btn)
            
            # 4. Wait for OTP or Next Step
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'OTP')] | //input[@type='password']")))
            
            # If we reach here, the UI submitted successfully
            result["status"] = "passed (UI Submission successful)"
            
        except Exception as e:
            result["errors"] = str(e)
            if driver:
                os.makedirs("screenshots", exist_ok=True)
                screenshot_file = f"screenshots/failure_{browser}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                driver.save_screenshot(screenshot_file)
                result["screenshot_path"] = screenshot_file
        finally:
            if driver:
                driver.quit()
                
        all_results.append(result)
        
    return all_results

if __name__ == "__main__":
    print("=========================================")
    print("       STARTING SIGNUP TEST SUITE        ")
    print("=========================================\n")
    
    # 1. API Test
    print("Running API-Based Signup Test...")
    api_results = test_api_signup()
    print("API Test Results:")
    print(json.dumps(api_results, indent=2))
    
    print("\n" + "="*41 + "\n")
    
    # 2. Cross Browser Test
    print("Running Cross-Browser Signup Test...")
    # NOTE: To run this, ensure you have chromedriver, geckodriver, and msedgedriver installed
    # cb_results = test_cross_browser_signup()
    # print("Cross-Browser Test Results:")
    # print(json.dumps(cb_results, indent=2))
    print("Cross-Browser tests are commented out by default to prevent unexpected browser popups.")
    print("Uncomment `cb_results = test_cross_browser_signup()` in the script to run them.")
    
    # Write results to file
    final_output = {
        "api_results": api_results,
        # "cross_browser_results": cb_results
    }
    
    with open('signup_test_report.json', 'w') as f:
        json.dump(final_output, f, indent=2)
        
    print("\nResults exported to signup_test_report.json")
