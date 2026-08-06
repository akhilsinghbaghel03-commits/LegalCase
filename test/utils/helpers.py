import json
import time
import datetime
import random
import re
import urllib.request
import urllib.error
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def fill_field(driver, xpath, text, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        elements = driver.find_elements(By.XPATH, xpath)
        for element in elements:
            try:
                if element.is_displayed():
                    element.clear()
                    element.send_keys(text)
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    raise Exception(f"Could not find an interactable element for xpath within {timeout}s: {xpath}")

def fill_field_by_keyword(driver, keyword, text, timeout=10):
    keyword = keyword.lower()
    end_time = time.time() + timeout
    while time.time() < end_time:
        # First check inside popups, then fallback to all inputs
        elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'popup')]//input") + driver.find_elements(By.TAG_NAME, "input")
        for element in elements:
            try:
                if element.is_displayed():
                    ph = (element.get_attribute("placeholder") or "").lower()
                    id_attr = (element.get_attribute("id") or "").lower()
                    if keyword in ph or keyword in id_attr:
                        element.clear()
                        element.send_keys(text)
                        return True
            except Exception:
                pass
        time.sleep(0.5)
    raise Exception(f"Could not find an interactable input for keyword '{keyword}' within {timeout}s")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # chrome_options.add_argument("--headless") # Uncomment to run headlessly
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    return driver, wait

def safe_urlopen(req, max_retries=5):
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode()
        except (urllib.error.URLError, socket.gaierror, socket.timeout) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Network error: {e}. Retrying {attempt + 1}/{max_retries}...")
            time.sleep(5)

import http.cookiejar
guerrilla_cj = http.cookiejar.CookieJar()
guerrilla_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(guerrilla_cj))
guerrilla_opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

def get_mail_tm_domain():
    return "guerrillamail.com"

def create_mail_tm_account(email, password):
    prefix = email.split('@')[0]
    domain = get_mail_tm_domain()
    req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=set_email_user&email_user={prefix}&lang=en&domain={domain}', method='POST')
    try:
        return json.loads(guerrilla_opener.open(req).read().decode())
    except Exception as e:
        print(f"Failed to create GuerrillaMail account: {e}")
        return None

def get_mail_tm_token(email, password):
    return "guerrillamail_dummy_token"

def get_current_mail_ids(token=None):
    try:
        req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=check_email&seq=0')
        res = json.loads(guerrilla_opener.open(req).read().decode())
        return [msg['mail_id'] for msg in res.get('list', [])]
    except Exception:
        return []

def get_otp_from_mail_tm(token, max_retries=60, ignore_mail_ids=None):
    """Poll GuerrillaMail for an email containing a 6-digit or 4-digit OTP."""
    import re
    if ignore_mail_ids is None:
        ignore_mail_ids = []
        
    for i in range(max_retries):
        print(f"Polling for email... (Attempt {i+1}/{max_retries})")
        time.sleep(10)
        
        req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=check_email&seq=0')
        try:
            res = json.loads(guerrilla_opener.open(req).read().decode())
            for msg in res.get('list', []):  # Check newest first
                msg_id = msg['mail_id']
                if msg_id in ignore_mail_ids:
                    continue
                    
                msg_req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={msg_id}')
                msg_res = json.loads(guerrilla_opener.open(msg_req).read().decode())
                body = msg_res.get('mail_body', '')
                subject = msg.get('mail_subject', '')
                
                print(f"  -> Found email with subject: '{subject}'")
                if 'welcome to guerrilla mail' in subject.lower():
                    continue
                
                # Strip HTML tags to avoid matching hex color codes or URLs
                plain_text = re.sub(r'<[^>]+>', ' ', body)
                
                # Extract OTP
                # Use negative lookbehind to ensure the number is NOT preceded by '#' (a hex code) or a word character
                otp_match = re.search(r'(?<![#\w])(\d{6})(?!\w)', plain_text)
                if not otp_match:
                    otp_match = re.search(r'(?<![#\w])(\d{4})(?!\w)', plain_text)
                    
                if otp_match:
                    otp = otp_match.group(1)
                    return otp, msg_id
        except Exception as e:
            print(f"API polling error: {e}")
            
    return None

def delete_mail_tm_messages(token):
    print("Clearing old messages from GuerrillaMail inbox...")
    try:
        req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=check_email&seq=0')
        res = json.loads(guerrilla_opener.open(req).read().decode())
        email_ids = [msg['mail_id'] for msg in res.get('list', [])]
        if email_ids:
            for eid in email_ids:
                del_req = urllib.request.Request(f'http://api.guerrillamail.com/ajax.php?f=del_email&email_ids[]={eid}', method='POST')
                guerrilla_opener.open(del_req)
            print(f"Deleted {len(email_ids)} messages.")
    except Exception as e:
        print(f"Failed to clear inbox: {e}")

def fill_stripe_form(driver, wait):
    print("Waiting for redirection to Stripe Checkout...")
    try:
        wait.until(EC.url_contains("stripe.com"))
    except Exception as e:
        print(f"Warning: Did not redirect to stripe.com within timeout: {e}")
        
    time.sleep(5)
    
    try:
        driver.switch_to.default_content()
        card_num = driver.find_element(By.XPATH, "//input[@autocomplete='cc-number' or @name='cardNumber' or contains(@placeholder, '1234') or @name='numberInput']")
        card_num.send_keys("4242424242424242")
        
        exp_date = driver.find_element(By.XPATH, "//input[@autocomplete='cc-exp' or @name='cardExpiry' or contains(@placeholder, 'MM / YY') or contains(@placeholder, 'MM/YY')]")
        exp_date.send_keys("0726")
        
        cvc = driver.find_element(By.XPATH, "//input[@autocomplete='cc-csc' or @name='cardCvc' or contains(@placeholder, 'CVC')]")
        cvc.send_keys("123")
        
        try:
            stripe_email = driver.find_element(By.XPATH, "//input[@type='email' or @autocomplete='email' or @name='email' or contains(@placeholder, 'email')]")
            stripe_email.send_keys("akh@gmail.com")
        except: pass
        
        try:
            name_input = driver.find_element(By.XPATH, "//input[@autocomplete='cc-name' or @name='billingName' or contains(@placeholder, 'name')]")
            name_input.send_keys("Test User")
        except: pass
    except Exception as e:
        print(f"Fields not in main document. Searching iframes: {e}")
        all_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for idx, iframe in enumerate(all_iframes):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)
                try: driver.find_element(By.XPATH, "//input[@name='cardnumber' or @autocomplete='cc-number']").send_keys("4242424242424242")
                except: pass
                try: driver.find_element(By.XPATH, "//input[@name='exp-date' or @autocomplete='cc-exp']").send_keys("0726")
                except: pass
                try: driver.find_element(By.XPATH, "//input[@name='cvc' or @autocomplete='cc-csc']").send_keys("123")
                except: pass
            except: pass
        driver.switch_to.default_content()

    print("Clicking Final Submit Button...")
    try:
        submit_trial_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'SubmitButton')] | //button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pay')]")))
        driver.execute_script("arguments[0].click();", submit_trial_btn)
    except:
        try: driver.find_element(By.XPATH, "//button[@type='submit' or contains(@class, 'SubmitButton')]").click()
        except: pass
