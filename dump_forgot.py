import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def dump_forgot():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    
    driver.get("https://yorpro-test.outsystems.app/legalhub/Login")
    forgot_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Forgot Password')]")))
    driver.execute_script("arguments[0].click();", forgot_link)
    time.sleep(2)
    
    inputs = driver.find_elements(By.XPATH, "//input[@type='email' or @type='text']")
    print(f"Found {len(inputs)} text/email inputs on the page:")
    for idx, el in enumerate(inputs):
        print(f"Input {idx}: id='{el.get_attribute('id')}', type='{el.get_attribute('type')}', placeholder='{el.get_attribute('placeholder')}', displayed={el.is_displayed()}")
    
    driver.quit()

if __name__ == '__main__':
    dump_forgot()
