from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def run_scratch_invalid_login():
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get('https://yorpro-test.outsystems.app/legalhub/Login')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']"))).send_keys('nonexistent@domain.com')
        driver.find_element(By.XPATH, "//input[@id='Input_Password' or @type='password']").send_keys('WrongPassword123!')
        driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()
        time.sleep(3)
        try:
            error_el = driver.find_element(By.CSS_SELECTOR, '.feedback-message')
            print('Feedback Message:', error_el.text)
        except Exception as e:
            print('Could not find .feedback-message:', e)
        try:
            error_el = driver.find_element(By.CSS_SELECTOR, '.validation-message')
            print('Validation Message:', error_el.text)
        except Exception as e:
            print('Could not find .validation-message:', e)
        print('Page Text snippet:', driver.find_element(By.TAG_NAME, 'body').text[:500])
        driver.save_screenshot('invalid_login.png')
    finally:
        driver.quit()

if __name__ == '__main__':
    run_scratch_invalid_login()

