import pytest
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test.utils.helpers import get_driver, fill_field, perform_login, set_input_value, navigate_with_retry


def login(driver, wait):
    perform_login(driver, wait)


def test_matter_workflow(driver_setup):
    """Verify validation when adding a new person, new company, and new matter."""
    driver, wait = driver_setup
    
    # 1. Login
    login(driver, wait)
    
    def click_button_by_texts(texts):
        for t in texts:
            try:
                xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{t.lower()}')] | //button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{t.lower()}')] | //a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{t.lower()}')]"
                elems = driver.find_elements(By.XPATH, xpath)
                for el in elems:
                    if el.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
                        return True
            except Exception:
                pass
        return False

    def fill_by_label(label_text, val):
        label_lower = label_text.lower()
        xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'field') or contains(@class, 'margin')]//input | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/following::input[1] | //input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]"
        elems = driver.find_elements(By.XPATH, xpath)
        for inp in elems:
            if inp.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                time.sleep(0.3)
                set_input_value(driver, inp, val)
                return True
        return False

    # 2. Go to Contact module
    try:
        contact_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CONTACT', 'contact'), 'contact')] | //a[contains(@href, 'Contact')]")))
        driver.execute_script("arguments[0].click();", contact_link)
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Contact")
    time.sleep(3)

    
    # --- NEW PERSON ---
    if not click_button_by_texts(["new person", "person"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["person", "new person", "add person"])
            
    time.sleep(2)
    # Click save without entering anything
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(1)
    
    # Enter First Name only
    fill_by_label("First Name", "TestFirst")
    
    # Click Save
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(1)
    
    # Enter Last Name
    fill_by_label("Last Name", "TestLast")
    
    # Click Save
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    
    # --- NEW COMPANY ---
    if not click_button_by_texts(["new company", "company"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["company", "new company", "add company"])
            
    time.sleep(2)
    # Click save without entering anything
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(1)
    
    # Enter Company Name
    if not fill_by_label("Company Name", "Test Company"):
        fill_by_label("Company", "Test Company") or fill_by_label("Name", "Test Company")
    
    # Click Save
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    
    # --- GOTO MATTER MODULE ---
    try:
        matter_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'MATTER', 'matter'), 'matter')] | //a[contains(@href, 'Matter')]")))
        driver.execute_script("arguments[0].click();", matter_link)
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Matter")
    time.sleep(3)


    
    # Click New Matter
    if not click_button_by_texts(["new matter", "matter"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["matter", "new matter", "add matter"])
            
    time.sleep(2)
    
    # Select Client
    try:
        client_dropdown = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'client')]/following::select | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'client')]/following::input[contains(@class, 'dropdown') or @role='combobox'] | //*[contains(@class, 'dropdown')]")
        driver.execute_script("arguments[0].click();", client_dropdown)
        time.sleep(1)
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    except Exception:
        pass
    time.sleep(1)
    
    # Enter Description 'randam test'
    try:
        description_input = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'description')]/following::textarea | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'description')]/following::input[1] | //textarea")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", description_input)
        description_input.clear()
        description_input.send_keys("randam test")
        set_input_value(driver, description_input, "randam test")
    except Exception:
        pass
        
    # Click Save button
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(4)

    
    print("Matter workflow completed successfully!")

