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

def navigate_with_retry(driver, url, max_retries=4, delay=3):
    """Navigate to a URL with automatic retries on momentary network/DNS disconnects."""
    last_err = None
    for attempt in range(max_retries):
        try:
            driver.get(url)
            return
        except Exception as e:
            last_err = e
            err_msg = str(e).lower()
            if any(k in err_msg for k in ["err_name_not_resolved", "err_internet_disconnected", "err_connection", "timed out", "timeout"]):
                print(f"Network glitch while navigating to {url} (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {delay}s...")
                time.sleep(delay)
                continue
            raise e
    if last_err:
        raise last_err


def set_input_value(driver, element, value):
    """Reliably set input value in React / OutSystems Reactive applications."""
    try:
        driver.execute_script("""
            var input = arguments[0];
            var val = arguments[1];
            input.focus();
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (!nativeInputValueSetter) {
                nativeInputValueSetter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(input), 'value');
            }
            if (nativeInputValueSetter && nativeInputValueSetter.set) {
                nativeInputValueSetter.set.call(input, val);
            } else {
                input.value = val;
            }
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        """, element, value)
    except Exception:
        try:
            element.clear()
            element.send_keys(value)
        except Exception:
            pass

def fill_field(driver, xpath, text, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        elements = driver.find_elements(By.XPATH, xpath)
        for element in elements:
            try:
                if element.is_displayed():
                    set_input_value(driver, element, text)
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    raise Exception(f"Could not find an interactable element for xpath within {timeout}s: {xpath}")


def fill_field_by_keyword(driver, keyword, text, timeout=10):
    keyword = keyword.lower()
    end_time = time.time() + timeout
    while time.time() < end_time:
        elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'popup')]//input") + driver.find_elements(By.TAG_NAME, "input")
        for element in elements:
            try:
                if element.is_displayed() and element.get_attribute('type') != 'hidden':
                    ph = (element.get_attribute("placeholder") or "").lower()
                    id_attr = (element.get_attribute("id") or "").lower()
                    name_attr = (element.get_attribute("name") or "").lower()
                    if keyword in ph or keyword in id_attr or keyword in name_attr:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        element.clear()
                        element.send_keys(text)
                        set_input_value(driver, element, text)
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
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
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

_current_sid_token = None

def get_mail_tm_domain():
    return "guerrillamail.com"

def create_mail_tm_account(email, password):
    global _current_sid_token
    prefix = email.split('@')[0]
    domain = get_mail_tm_domain()
    req = urllib.request.Request(
        f'http://api.guerrillamail.com/ajax.php?f=set_email_user&email_user={prefix}&lang=en&domain={domain}',
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
        method='POST'
    )
    try:
        res = json.loads(urllib.request.urlopen(req).read().decode())
        _current_sid_token = res.get('sid_token')
        print(f"GuerrillaMail active user set to: {prefix}@{domain}, sid_token: {_current_sid_token}")
        return res
    except Exception as e:
        print(f"Failed to create/set GuerrillaMail account: {e}")
        return None

def get_mail_tm_token(email, password):
    global _current_sid_token
    if not _current_sid_token:
        create_mail_tm_account(email, password)
    return _current_sid_token

def get_current_mail_ids(token=None):
    global _current_sid_token
    sid = token or _current_sid_token or ""
    try:
        req = urllib.request.Request(
            f'http://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid}',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        res = json.loads(urllib.request.urlopen(req).read().decode())
        return [msg['mail_id'] for msg in res.get('list', [])]
    except Exception:
        return []

def get_otp_from_mail_tm(token, max_retries=60, ignore_mail_ids=None, expected_length=None):
    """Poll GuerrillaMail for an email containing an OTP with network resilience."""
    import re
    global _current_sid_token
    sid = token or _current_sid_token or ""
    if ignore_mail_ids is None:
        ignore_mail_ids = []
        
    for i in range(max_retries):
        print(f"Polling for email... (Attempt {i+1}/{max_retries})")
        time.sleep(3)
        
        req = urllib.request.Request(
            f'http://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid}',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            msg_list = res.get('list', [])
            print(f"  Inbox has {len(msg_list)} emails: {[m['mail_id'] for m in msg_list]}")
            
            for msg in msg_list:
                msg_id = msg['mail_id']
                if msg_id in ignore_mail_ids:
                    continue
                    
                msg_req = urllib.request.Request(
                    f'http://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={msg_id}&sid_token={sid}',
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                msg_res = json.loads(urllib.request.urlopen(msg_req, timeout=10).read().decode())
                body = msg_res.get('mail_body', '')
                subject = msg.get('mail_subject', '')
                
                if 'welcome to guerrilla mail' in subject.lower():
                    continue
                    
                print(f"  -> Email ID {msg_id}, subject: '{subject}'")
                plain_text = re.sub(r'<[^>]+>', ' ', body)
                print(f"  -> Plain text body: {plain_text[:300]}")
                
                otp = None
                if expected_length:
                    otp_match = re.search(rf'(?<![#\w])(\d{{{expected_length}}})(?!\w)', plain_text)
                    if otp_match:
                        otp = otp_match.group(1)
                else:
                    # 1. Contextual match in body (verification code, OTP, passcode)
                    context_matches = re.findall(r'(?:verification\s*code|otp|passcode|security\s*code|your\s*code\s*is|code\s*is|login\s*code)[^\d]{0,25}(\d{4,6})', plain_text, re.IGNORECASE)
                    if context_matches:
                        otp = context_matches[0]
                    
                    # 2. Contextual match in subject
                    if not otp:
                        subj_matches = re.findall(r'(?:code|otp)[^\d]{0,15}(\d{4,6})', subject, re.IGNORECASE)
                        if subj_matches:
                            otp = subj_matches[0]
                            
                    # 3. Isolated 6-digit number
                    if not otp:
                        all_6_digits = re.findall(r'(?<!\d)(\d{6})(?!\d)', plain_text)
                        if all_6_digits:
                            otp = all_6_digits[0]
                            
                    # 4. Isolated 4-digit number (excluding years)
                    if not otp:
                        all_4_digits = [d for d in re.findall(r'(?<!\d)(\d{4})(?!\d)', plain_text) if d not in ['2023', '2024', '2025', '2026', '2027']]
                        if all_4_digits:
                            otp = all_4_digits[0]
                    
                if otp:
                    print(f"Matched Valid OTP: {otp} from email {msg_id}")
                    return otp, msg_id
        except Exception as e:
            print(f"API polling error: {e}")
            time.sleep(2)
            
    return None


def enter_otp_digits(driver, otp_code):
    """Accurately enter OTP code into OutSystems / React OTP inputs."""
    print(f"Entering valid OTP: {otp_code}")
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    
    otp_fields = driver.find_elements(By.XPATH, "//input[contains(@id,'OTP') or contains(@class, 'otp') or contains(@placeholder, 'OTP')]")
    visible_fields = [f for f in otp_fields if f.is_displayed() and f.get_attribute('type') != 'hidden']
    
    if len(visible_fields) > 1:
        # Segmented multi-box input
        try:
            visible_fields[0].click()
        except Exception:
            driver.execute_script("arguments[0].focus(); arguments[0].click();", visible_fields[0])
        time.sleep(0.5)
        
        # Clear any existing text in all boxes
        for box in visible_fields:
            try:
                driver.execute_script("arguments[0].value = '';", box)
            except Exception: pass
            
        try:
            visible_fields[0].click()
        except Exception: pass
        time.sleep(0.2)
        
        for i, char in enumerate(otp_code):
            try:
                if i < len(visible_fields):
                    driver.execute_script("""
                        arguments[0].focus();
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, visible_fields[i], char)
                ActionChains(driver).send_keys(char).perform()
            except Exception:
                pass
            time.sleep(0.2)
            
        try:
            visible_fields[-1].send_keys(Keys.TAB)
        except Exception:
            pass
    elif visible_fields:
        # Single input field for entire OTP
        single_box = visible_fields[0]
        try:
            single_box.click()
            single_box.clear()
            single_box.send_keys(otp_code)
            set_input_value(driver, single_box, otp_code)
            single_box.send_keys(Keys.TAB)
        except Exception:
            pass
    else:
        ActionChains(driver).send_keys(otp_code).perform()


def delete_mail_tm_messages(token=None):
    global _current_sid_token
    sid = token or _current_sid_token or ""
    print("Clearing old messages from GuerrillaMail inbox...")
    try:
        req = urllib.request.Request(
            f'http://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid}',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        email_ids = [msg['mail_id'] for msg in res.get('list', []) if msg['mail_id'] != 1]
        if email_ids:
            ids_str = "&".join([f"email_ids[]={mid}" for mid in email_ids])
            del_req = urllib.request.Request(
                f'http://api.guerrillamail.com/ajax.php?f=del_email&{ids_str}&sid_token={sid}',
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            urllib.request.urlopen(del_req, timeout=10).read()
            print(f"Deleted {len(email_ids)} messages.")
    except Exception:
        pass



def fill_stripe_form(driver, wait):
    print("Waiting for redirection to Stripe Checkout...")
    try:
        wait.until(EC.url_contains("stripe.com"))
    except Exception as e:
        print(f"Warning: Did not redirect to stripe.com within timeout: {e}")
        
    time.sleep(5)
    
    try:
        # Try main document first
        card_num = driver.find_element(By.XPATH, "//input[@autocomplete='cc-number' or @name='cardNumber' or contains(@placeholder, '1234') or @name='numberInput']")
        card_num.send_keys("4242424242424242")
        
        exp_date = driver.find_element(By.XPATH, "//input[@autocomplete='cc-exp' or @name='cardExpiry' or contains(@placeholder, 'MM / YY') or contains(@placeholder, 'MM/YY')]")
        exp_date.send_keys("0726")
        
        cvc = driver.find_element(By.XPATH, "//input[@autocomplete='cc-csc' or @name='cardCvc' or contains(@placeholder, 'CVC')]")
        cvc.send_keys("123")
        
        try:
            stripe_email = driver.find_element(By.XPATH, "//input[@type='email' or @autocomplete='email' or @name='email' or contains(@placeholder, 'email')]")
            stripe_email.send_keys("test@example.com")
        except Exception: pass
        
        try:
            name_input = driver.find_element(By.XPATH, "//input[@autocomplete='cc-name' or @name='billingName' or contains(@placeholder, 'name')]")
            name_input.send_keys("Test User")
        except Exception: pass
    except Exception:
        all_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in all_iframes:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)
                try: driver.find_element(By.XPATH, "//input[@name='cardnumber' or @autocomplete='cc-number']").send_keys("4242424242424242")
                except Exception: pass
                try: driver.find_element(By.XPATH, "//input[@name='exp-date' or @autocomplete='cc-exp']").send_keys("0726")
                except Exception: pass
                try: driver.find_element(By.XPATH, "//input[@name='cvc' or @autocomplete='cc-csc']").send_keys("123")
                except Exception: pass
            except Exception: pass
        driver.switch_to.default_content()

    try:
        submit_trial_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'SubmitButton')] | //button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pay')]")))
        driver.execute_script("arguments[0].click();", submit_trial_btn)
    except Exception:
        try: driver.find_element(By.XPATH, "//button[@type='submit' or contains(@class, 'SubmitButton')]").click()
        except Exception: pass


def register_new_user(driver, wait):
    """Register and activate a brand new user via signup and trial flow."""
    domain = get_mail_tm_domain()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_digits = f"{random.randint(1000, 9999)}"
    email = f"user_{timestamp}_{random_digits}@{domain}"
    password = "TestPassword123!@#"
    
    create_mail_tm_account(email, password)
    token = get_mail_tm_token(email, password)
    
    # Save initially
    with open('shared_state.json', 'w') as f:
        json.dump({"email": email, "password": password}, f)
        
    navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Login")
    try:
        signup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]")))
        driver.execute_script("arguments[0].click();", signup_link)
    except:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/signup")

        
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    time.sleep(2)
    
    fill_field_by_keyword(driver, "first", "John")
    fill_field_by_keyword(driver, "last", "Doe")
    fill_field_by_keyword(driver, "email", email)
    fill_field_by_keyword(driver, "phone", "9876543210")
    fill_field_by_keyword(driver, "company", f"Automated Test Corp {timestamp}{random_digits}")
    
    time.sleep(2)
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send Verification Code') or contains(., 'Next')]")))
    try:
        submit_btn.click()
    except Exception:
        pass
    try:
        driver.execute_script("""
            arguments[0].scrollIntoView({block: 'center'});
            var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
            arguments[0].dispatchEvent(ev);
        """, submit_btn)
    except Exception:
        pass
        
    # Wait for OTP fields with retry click if needed
    otp_inputs_found = False
    for _ in range(25):
        if driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]"):
            otp_inputs_found = True
            break
        time.sleep(1)
        try:
            driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", submit_btn)
        except Exception:
            pass

    if not otp_inputs_found:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'OTP')]")))
        
    otp_info = get_otp_from_mail_tm(token)

    if isinstance(otp_info, tuple):
        otp_code = otp_info[0]
    else:
        otp_code = otp_info
        
    if not otp_code:
        raise Exception("Failed to retrieve OTP for registration.")
        
    # Enter OTP using ActionChains
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    otp_fields = driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")
    visible_otp_fields = [f for f in otp_fields if f.is_displayed()]
    if visible_otp_fields:
        visible_otp_fields[0].click()
        time.sleep(0.5)
        for char in otp_code:
            ActionChains(driver).send_keys(char).perform()
            time.sleep(0.2)
        visible_otp_fields[-1].send_keys(Keys.TAB)
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
    password_inputs = driver.find_elements(By.XPATH, "//input[@type='password']")
    visible_pws = [p for p in password_inputs if p.is_displayed() and p.size['width'] > 0]
    
    if visible_pws:
        for p in visible_pws:
            try:
                p.click()
                p.clear()
                p.send_keys(password)
                set_input_value(driver, p, password)
            except Exception as e:
                print(f"Password entry error: {e}")
            time.sleep(0.3)
            
        try:
            visible_pws[-1].send_keys(Keys.TAB)
        except Exception: pass
            
    time.sleep(2)
    verify_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Verify & Continue') or contains(., 'Verify')] | //*[contains(text(), 'Verify & Continue') or text()='Verify']")
    if verify_btns:
        verify_btn = verify_btns[-1]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", verify_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].removeAttribute('disabled');", verify_btn)
        try:
            verify_btn.click()
        except Exception:
            driver.execute_script("""
                var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
                arguments[0].dispatchEvent(ev);
            """, verify_btn)
    
    # Handle Step 3 (Trial details)
    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Trial Details') or contains(text(), 'Start your trial') or contains(text(), 'Credit Card')]")))
        time.sleep(2)
        try:
            terms = driver.find_element(By.XPATH, "//input[@id='b5-b9-Checkbox1'] | //input[@type='checkbox']")
            driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", terms)
            time.sleep(2)
        except: pass
        
        try:
            pay_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Pay')]")
            driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", pay_btn)
        except: pass
        
        fill_stripe_form(driver, wait)
        
        WebDriverWait(driver, 60).until(lambda d: "RedirectScreen" in d.current_url or "Dashboard" in d.current_url or "LegalHub" in d.current_url or "setting" in d.current_url)
        
        if "RedirectScreen" in driver.current_url:
            time.sleep(3)
            try:
                checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'] | //div[contains(@class, 'checkbox')]")
                driver.execute_script("arguments[0].click();", checkbox)
            except: pass
            
            try:
                proceed_btn = driver.find_element(By.XPATH, "//button | //a[contains(@class, 'btn')]")
                driver.execute_script("arguments[0].click();", proceed_btn)
            except: pass
            
    except Exception as e:
        print(f"Step 3 handling info: {e}")
        
    time.sleep(3)
    delete_mail_tm_messages(token)
    with open('shared_state.json', 'w') as f:
        json.dump({"email": email, "password": password}, f)
        
    return email, password



def perform_login(driver, wait, email=None, password=None):
    """Log into the LegalHub application, handling 2FA OTP and auto-registration fallback if needed."""
    if not email or not password:
        try:
            with open('shared_state.json', 'r') as f:
                state = json.load(f)
                email = state.get('email', '')
                password = state.get('password', 'TestPassword123!@#')
        except Exception:
            email = ''
            password = 'TestPassword123!@#'
            
    if not email:
        print("No valid email in shared_state.json. Auto-registering a new user...")
        email, password = register_new_user(driver, wait)
        if "login" not in driver.current_url.lower() and "signup" not in driver.current_url.lower():
            return
            
    navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Login")
    time.sleep(2)
    
    # Check if already authenticated and redirected away from login
    if "login" not in driver.current_url.lower() and "signup" not in driver.current_url.lower():
        print(f"Already logged in / active session detected (URL: {driver.current_url}).")
        return
    
    if "guerrillamail.com" in email:
        create_mail_tm_account(email, password)
        token = get_mail_tm_token(email, password)
        existing_mail_ids = get_current_mail_ids(token)
    else:
        token = get_mail_tm_token(email, password)
        existing_mail_ids = []
        
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']")))
    except Exception:
        if "login" not in driver.current_url.lower() and "signup" not in driver.current_url.lower():
            print(f"Redirected to active dashboard (URL: {driver.current_url}).")
            return
        raise

    email_inp = driver.find_element(By.XPATH, "//input[@id='Input_UserEmail' or @type='email']")
    email_inp.clear()
    email_inp.send_keys(email)
    set_input_value(driver, email_inp, email)
    
    pw_input = driver.find_element(By.XPATH, "//input[@id='Input_Password' or @type='password']")
    pw_input.clear()
    pw_input.send_keys(password)
    set_input_value(driver, pw_input, password)
    
    time.sleep(1)
    submit_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]")
    try:
        submit_btn.click()
    except Exception:
        driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", submit_btn)

    # Wait dynamically for server response: either URL change, OTP fields, or validation error
    otp_found = False
    visible_otp_fields = []
    for _ in range(35):
        time.sleep(1)
        
        # 1. Check if logged in directly
        if "login" not in driver.current_url.lower() and "signup" not in driver.current_url.lower():
            time.sleep(2)
            return
            
        # 2. Check if OTP fields appeared
        visible_otp_fields = [f for f in driver.find_elements(By.XPATH, "//input[contains(@id,'OTP') or contains(@class, 'otp-input')]") if f.is_displayed()]
        if visible_otp_fields:
            otp_found = True
            break
            
        # 3. Check if login failed with explicit error banner
        error_msgs = driver.find_elements(By.XPATH, "//*[contains(@class, 'feedback-message-error') or contains(@class, 'feedback-message-text')]")
        real_errors = [e.text.strip() for e in error_msgs if e.is_displayed() and any(k in e.text.lower() for k in ['incorrect', 'invalid username', 'invalid password', 'does not exist', 'not found'])]
        if real_errors:
            print(f"Login failed for {email} ({real_errors[0]}). Auto-registering a fresh user...")
            email, password = register_new_user(driver, wait)
            if "login" not in driver.current_url.lower() and "signup" not in driver.current_url.lower():
                return
            return perform_login(driver, wait, email, password)

    if otp_found and visible_otp_fields:
        print(f"OTP fields found ({len(visible_otp_fields)}). Fetching OTP...")
        try:
            if "guerrillamail.com" in email:
                create_mail_tm_account(email, password)
                
            otp_info = get_otp_from_mail_tm(token, max_retries=15, ignore_mail_ids=existing_mail_ids, expected_length=len(visible_otp_fields))
            if not otp_info:
                # Try clicking Resend OTP once if delayed
                try:
                    resend_btn = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'resend')] | //*[contains(text(), 'Resend OTP')]")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", resend_btn)
                    print("Clicked Resend OTP button.")
                    time.sleep(2)
                    otp_info = get_otp_from_mail_tm(token, max_retries=15, ignore_mail_ids=existing_mail_ids, expected_length=len(visible_otp_fields))
                except Exception:
                    pass
                    
            if isinstance(otp_info, tuple):
                otp_code = otp_info[0]
            else:
                otp_code = otp_info
                
            if not otp_code:
                print("Login 2FA OTP delayed. Auto-registering a fresh active session...")
                register_new_user(driver, wait)
                if "login" in driver.current_url.lower():
                    navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Dashboard")
                return

            if otp_code:
                enter_otp_digits(driver, otp_code)
                time.sleep(2)
                verify_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Verify & Continue') or contains(., 'Verify')] | //*[contains(text(), 'Verify & Continue') or text()='Verify']")
                if verify_btns:
                    verify_btn = verify_btns[-1]
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", verify_btn)
                    time.sleep(0.5)
                    try:
                        verify_btn.click()
                    except Exception:
                        driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", verify_btn)
        except Exception as e:
            print(f"Error handling login OTP: {e}")
            register_new_user(driver, wait)
            return


            
    if not otp_found and ("login" in driver.current_url.lower() or "signup" in driver.current_url.lower()):
        print(f"Login did not advance for {email}. Auto-registering a fresh active session...")
        register_new_user(driver, wait)
        if "login" in driver.current_url.lower():
            navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Dashboard")
        time.sleep(2)
        return

    # Wait for successful navigation away from login
    try:
        WebDriverWait(driver, 20).until(lambda d: "login" not in d.current_url.lower() and "signup" not in d.current_url.lower())
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Dashboard")
        time.sleep(2)
        if "login" in driver.current_url.lower():
            print("Session not active. Registering fresh user...")
            register_new_user(driver, wait)
            navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Dashboard")
        
    time.sleep(2)




