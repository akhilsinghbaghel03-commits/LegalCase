import time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
sys.path.append('c:/Users/dell/Akhil_AI')
from test.utils.helpers import get_mail_tm_token, get_otp_from_mail_tm

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    print('Logging in...')
    driver.get('https://yorpro-test.outsystems.app/legalhub/Login')
    email = 'user_20260727134005_1034@web-library.net'
    pw = 'TestPassword123!@#'
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))).send_keys(email)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(pw)
    print('Clearing old OTP emails...')
    token = get_mail_tm_token(email, pw)
    from test.run_signup import delete_mail_tm_messages
    delete_mail_tm_messages(token)

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[@type='submit']"))
    
    print('Getting OTP...')
    time.sleep(5)
    otp = get_otp_from_mail_tm(token)
    print(f'OTP: {otp}')
    
    otp_fields = driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")
    visible_otp_fields = [f for f in otp_fields if f.is_displayed()]
    for i, c in enumerate(otp):
        visible_otp_fields[i].send_keys(c)
        time.sleep(0.1)
        
    verify_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Verify & Continue') or text()='Verify']")
    driver.execute_script("var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); arguments[0].dispatchEvent(ev);", verify_btn)
    
    wait.until(lambda d: 'Dashboard' in d.current_url or 'LegalHub' in d.current_url)
    print('Logged in!')
    time.sleep(5)
    
    # Wait for Dashboard module and click Contact
    driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CONTACT', 'contact'), 'contact')] | //a[contains(@href, 'Contact')]"))))
    time.sleep(3)
    
    # Click New Person
    try:
        new_person_btn = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'new person') or text()='Person']")
        driver.execute_script("arguments[0].click();", new_person_btn)
    except:
        add_entry = driver.find_element(By.XPATH, "//*[contains(text(), 'Add New Entry') or contains(@class, 'new-entry')]")
        driver.execute_script("arguments[0].click();", add_entry)
        time.sleep(1)
        person_option = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'new person') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add person') or text()='Person']")
        driver.execute_script("arguments[0].click();", person_option)
        
    time.sleep(3)
    print("Filling New Person form...")

    def fill_by_label(label_text, val):
        try:
            inp = driver.find_element(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_text.lower()}')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'field')]//input | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_text.lower()}')]/following::input[1]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
            time.sleep(0.5)
            inp.clear()
            inp.send_keys(val)
            print(f"Filled {label_text} successfully.")
        except Exception as e:
            print(f"Warning: Could not fill {label_text}: {e}")

    fill_by_label("First Name", "Jane")
    fill_by_label("Last Name", "Smith")
    fill_by_label("Email", "jane.smith@example.com")
    fill_by_label("Phone", "1234567890")

    # Tags
    print("Handling Tags...")
    try:
        add_tag_btn = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'TAG', 'tag'), 'add tag') or contains(text(), 'Add Tag')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", add_tag_btn)
        time.sleep(2)
        
        tag_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'tag') or contains(@class, 'tag')]")
        tag_input.send_keys("TestTag")
        time.sleep(1)
        
        create_tag_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Add')]")
        driver.execute_script("arguments[0].click();", create_tag_btn)
        time.sleep(2)
        
        cross_btn = driver.find_element(By.XPATH, "//*[contains(@class, 'close') or text()='x' or text()='X']")
        driver.execute_script("arguments[0].click();", cross_btn)
        time.sleep(1)
        
        driver.execute_script("arguments[0].click();", add_tag_btn)
        time.sleep(1)
        tag_option = driver.find_element(By.XPATH, "//*[contains(text(), 'TestTag')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", tag_option)
    except Exception as e:
        print(f"Warning: Could not handle tagging: {e}")

    # Save
    print("Saving new contact...")
    try:
        save_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'SAVE', 'save'), 'save')]")
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(5)
        print("Contact saved successfully!")
    except Exception as e:
        print(f"Warning: Could not click save button: {e}")

    driver.save_screenshot('new_person_success.png')
    print('Saved new_person_success.png')
except Exception as e:
    print('Error:', e)
    try:
        driver.save_screenshot('debug_error.png')
        with open('debug_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Saved debug_error.png and debug_error.html")
    except:
        pass
finally:
    driver.quit()
