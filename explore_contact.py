import time
from test.utils.helpers import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver, wait = get_driver()
try:
    driver.get('https://yorpro-test.outsystems.app/legalhub/Login')
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))).send_keys('user_20260723180742@web-library.net')
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys('TestPassword123!@#')
    driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Log')]").click()
    
    wait.until(lambda d: 'Dashboard' in d.current_url or 'legalhub' in d.current_url)
    time.sleep(5)
    
    # Click Contacts
    contact_link = driver.find_element(By.XPATH, "//a[contains(@href, 'Contacts') or contains(@href, 'contact') or contains(., 'Contacts') or contains(., 'Contact')]")
    driver.execute_script("arguments[0].click();", contact_link)
    
    time.sleep(5)
    
    # Look for button texts
    buttons = driver.find_elements(By.XPATH, "//button | //a | //div[@role='button'] | //span[@role='button']")
    for b in buttons:
        if b.is_displayed():
            t = b.text.strip()
            if 'add' in t.lower() or 'new' in t.lower() or 'person' in t.lower():
                print('Found clickable with text:', t, b.get_attribute('class'))
                
except Exception as e:
    print('Error:', e)
finally:
    driver.quit()
