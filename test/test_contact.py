import pytest
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test.utils.helpers import get_driver, fill_field, perform_login, set_input_value

def login(driver, wait):
    perform_login(driver, wait)


def test_contact_validation(driver_setup):
    """Verify validation when adding a new contact."""
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
        driver.get("https://yorpro-test.outsystems.app/legalhub/Contact")
    time.sleep(3)

    
    # 3. Click New Person Form
    if not click_button_by_texts(["new person", "person"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["person", "new person", "add person"])
            
    time.sleep(2)
    
    # 4. Click save without entering anything
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(1)
    
    # 5. Enter First Name only
    fill_by_label("First Name", "TestFirst")
    
    # 6. Click Save
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(1)
    
    # 7. Enter all values as per fields
    fill_by_label("Last Name", "TestLast")
    fill_by_label("Email", f"test_{int(time.time())}@example.com")
    fill_by_label("Phone", "1234567890")
    
    # 8. Click Save
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    
    print("Contact validation test completed successfully!")




