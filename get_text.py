from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
driver.get('https://yorpro-test.outsystems.app/legalhub/Login')
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='Input_UserEmail' or @type='email']"))).send_keys('nonexistent@domain.com')
driver.find_element(By.XPATH, "//input[@id='Input_Password' or @type='password']").send_keys('WrongPassword123!')
driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()
time.sleep(3)
print(driver.find_element(By.TAG_NAME, 'body').text)
driver.quit()
