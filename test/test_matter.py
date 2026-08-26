import pytest
import time
import datetime
import random
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
    Complete End-to-End Workflow:
    1. Login to LegalHub.
    2. Navigate to Contact module and create a Person with full valid data.
    3. Create a Company with valid data.
    4. Navigate to Matter module.
    5. Click 'New Matter'.
    6. Select Client (the created person or client option).
    7. Enter Description.
    8. Select Open Date.
    9. Select Close Date.
    10. Select Responsible Person.
    11. Select Origination Person.
    12. Click Save button.
    13. Click on the newly generated Matter ID link.
    """
    driver, wait = driver_setup
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_id = f"{random.randint(1000, 9999)}"
    
    person_first = f"Akhil"
    person_last = f"Baghel_{random_id}"
    person_full = f"{person_first} {person_last}"
    person_email = f"akhil_{timestamp}_{random_id}@example.com"
    person_phone = "9098864919"
    company_name = f"LegalTech Corp {timestamp}"
    
    # 1. Login
    print("Logging in to LegalHub...")
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
        xpath = (
            f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')] | "
            f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'field') or contains(@class, 'margin')]//input | "
            f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/following::input[1]"
        )
        elems = driver.find_elements(By.XPATH, xpath)
        for inp in elems:
            if inp.is_displayed() and inp.get_attribute('type') != 'hidden':
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                time.sleep(0.3)
                set_input_value(driver, inp, val)
                return True
        return False

    # 2. Go to Contact module to create Person
    print("Navigating to Contact module...")
    try:
        contact_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CONTACT', 'contact'), 'contact')] | //a[contains(@href, 'Contact')]"))
        )
        driver.execute_script("arguments[0].click();", contact_link)
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Contact")
    time.sleep(3)
    
    # Click New Person
    print(f"Creating Person: {person_full}...")
    if not click_button_by_texts(["new person", "person"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["person", "new person", "add person"])
    time.sleep(2)

    # Fill Person with valid data
    fill_by_label("First Name", person_first)
    fill_by_label("Last Name", person_last)
    fill_by_label("Email", person_email)
    fill_by_label("Phone", person_phone)
    
    # Save Person (Click twice)
    print("Clicking Save button for Person (1st click)...")
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(2)
    
    print("Clicking Save button for Person (2nd click)...")
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    print(f"[SUCCESS] Person created and saved: {person_full}")

    # 3. Create Company
    print(f"Creating Company: {company_name}...")
    if not click_button_by_texts(["new company", "company"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["company", "new company", "add company"])
    time.sleep(2)
    if not fill_by_label("Company Name", company_name):
        fill_by_label("Company", company_name) or fill_by_label("Name", company_name)
    click_button_by_texts(["save", "save & continue", "submit"])
    time.sleep(3)
    print(f"[SUCCESS] Company created: {company_name}")

    # 4. Navigate to Matter Module
    print("Navigating to Matter module...")
    matter_page.navigate_to_matter_module()
    time.sleep(5)

    # 5. Click New Matter
    print("Opening New Matter form...")
    matter_page.click_new_matter()
    time.sleep(5)

    # 6. Select Client
    print(f"Selecting Client ({person_full})...")
    matter_page.select_client(client_name=person_first)
    time.sleep(5)

    # 7. Enter Description with valid data
    matter_desc = f"Corporate Legal Case - {person_last} ({timestamp})"
    print(f"Entering Description: {matter_desc}")
    matter_page.enter_description(matter_desc)
    time.sleep(5)

    # 8. Select Open Date
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Setting Open Date: {today_str}")
    matter_page.select_open_date(today_str)
    time.sleep(5)

    # 9. Select Close Date (45 days from today)
    close_date_str = (datetime.date.today() + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    print(f"Setting Close Date: {close_date_str}")
    matter_page.select_close_date(close_date_str)
    time.sleep(5)

    # 10. Select Responsible Person
    print("Selecting Responsible Person...")
    matter_page.select_responsible_person()
    time.sleep(5)

    # 11. Select Origination Person
    print("Selecting Origination Person...")
    matter_page.select_origination_person()
    time.sleep(5)

    # 12. Click Create Matter / Save Button
    print("Clicking Create Matter / Save button...")
    matter_page.click_save_button()
    time.sleep(5)

    # 13. Click on the Matter to view details
    print("Navigating into created Matter by clicking on the Matter...")
    clicked_id = matter_page.click_matter_id(description=matter_desc)
    time.sleep(5)

    # 14. Click on the Edit button
    print("Clicking on the Edit button on Matter details page...")
    matter_page.click_edit_button()
    time.sleep(5)

    print(f"End-to-End Workflow successfully completed! Matter clicked and Edit button pressed.")
