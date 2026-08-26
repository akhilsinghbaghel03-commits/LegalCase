import pytest
import time
import datetime
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test.utils.helpers import get_driver, fill_field, perform_login, set_input_value, navigate_with_retry
from Pages.matter_page import MatterPage


def login(driver, wait):
    perform_login(driver, wait)


def test_matter_workflow(driver_setup):
    """
    Test Matter Creation Workflow:
    1. Navigate to Matter module.
    2. Click 'New Matter'.
    3. Select Client.
    4. Enter Description.
    5. Select Open Date.
    6. Select Close Date.
    7. Select Responsible Person.
    8. Select Origination Person.
    9. Click Save button.
    10. Click on the Matter ID link to open details.
    """
    driver, wait = driver_setup
    
    # 1. Login
    login(driver, wait)
    time.sleep(2)

    matter_page = MatterPage(driver)
    
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

    # 2. Go to Contact module to ensure Person and Company exist
    try:
        contact_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CONTACT', 'contact'), 'contact')] | //a[contains(@href, 'Contact')]")))
        driver.execute_script("arguments[0].click();", contact_link)
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Contact")
    time.sleep(3)
    
    # Add Person
    if not click_button_by_texts(["new person", "person"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["person", "new person", "add person"])
    time.sleep(2)
    fill_by_label("First Name", "TestFirst")
    fill_by_label("Last Name", "TestLast")
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    
    # Add Company
    if not click_button_by_texts(["new company", "company"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["company", "new company", "add company"])
    time.sleep(2)
    if not fill_by_label("Company Name", "Test Company"):
        fill_by_label("Company", "Test Company") or fill_by_label("Name", "Test Company")
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)

    # 3. Navigate to Matter Module
    print("Navigating to Matter module...")
    matter_page.navigate_to_matter_module()
    time.sleep(3)

    # 4. Click New Matter
    print("Clicking New Matter button...")
    matter_page.click_new_matter()
    time.sleep(2)

    # 5. Select Client
    print("Selecting Client...")
    matter_page.select_client()
    time.sleep(1)

    # 6. Enter Description
    matter_desc = f"Matter Auto Test {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    print(f"Entering Description: {matter_desc}")
    matter_page.enter_description(matter_desc)
    time.sleep(1)

    # 7. Select Open Date
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Setting Open Date: {today_str}")
    matter_page.select_open_date(today_str)
    time.sleep(1)

    # 8. Select Close Date
    close_date_str = (datetime.date.today() + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    print(f"Setting Close Date: {close_date_str}")
    matter_page.select_close_date(close_date_str)
    time.sleep(1)

    # 9. Select Responsible Person
    print("Selecting Responsible Person...")
    matter_page.select_responsible_person()
    time.sleep(1)

    # 10. Select Origination Person
    print("Selecting Origination Person...")
    matter_page.select_origination_person()
    time.sleep(1)

    # 11. Click Save Button
    print("Clicking Save button...")
    matter_page.click_save_button()
    time.sleep(4)

    # 12. Click on the Matter ID to open details
    print("Clicking on Matter ID...")
    clicked_id = matter_page.click_matter_id(description=matter_desc)
    time.sleep(3)

    print(f"Matter creation and ID click completed! (Clicked Matter ID link: {clicked_id})")
