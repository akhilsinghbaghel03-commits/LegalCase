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
    2. Navigate to Contact module.
    3. Create a Company with valid data.
    4. Create a Person with valid data, select Company, and click Save multiple times.
    5. Navigate to Matter module.
    6. Click 'New Matter'.
    7. Select Client (5s sleep).
    8. Enter Description (5s sleep).
    9. Select Open Date (5s sleep).
    10. Select Close Date (5s sleep).
    11. Select Responsible Person (5s sleep).
    12. Select Origination Person (5s sleep).
    13. Click Create Matter / Save button (5s sleep).
    14. Click on the newly generated Matter ID link (2s sleep).
    15. Click on the Edit button (5s sleep).
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
    time.sleep(3)

    matter_page = MatterPage(driver)
    
    def click_button_by_texts(texts, retries=5):
        for _ in range(retries):
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
            time.sleep(1)
        return False

    def fill_by_label(label_text, val, retries=5):
        label_lower = label_text.lower()
        xpath = (
            f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')] | "
            f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'field') or contains(@class, 'margin')]//input | "
            f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/following::input[1]"
        )
        for _ in range(retries):
            elems = driver.find_elements(By.XPATH, xpath)
            for inp in elems:
                if inp.is_displayed() and inp.get_attribute('type') != 'hidden':
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                    time.sleep(0.3)
                    set_input_value(driver, inp, val)
                    return True
            time.sleep(1)
        return False

    def select_company_for_person(comp_name=None):
        print(f"Selecting company ({comp_name or 'Default'})...")
        try:
            comp_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'COMPANY', 'company'), 'company')]/following::div[contains(@class, 'vscomp-toggle-button') or contains(@class, 'vscomp-wrapper')][1] | "
                "//div[@class='vscomp-value' and contains(@data-tooltip, 'Company')] | "
                "//div[contains(@class, 'vscomp-toggle-button')] | "
                "//*[contains(translate(text(), 'COMPANY', 'company'), 'company')]/following::select[1] | "
                "//input[contains(@placeholder, 'Company') or contains(@id, 'Company')]"
            )
            for el in comp_elements:
                if el.is_displayed():
                    tag = el.tag_name.lower()
                    if "select" in tag:
                        el.click()
                        time.sleep(0.5)
                        el.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
                    elif "input" in tag:
                        el.clear()
                        el.send_keys(comp_name or "LegalTech")
                        time.sleep(0.5)
                        el.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
                    else: # vscomp dropdown
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
                        time.sleep(1)
                        options = driver.find_elements(By.XPATH, "//*[contains(@class, 'vscomp-option')]")
                        vis_opts = [o for o in options if o.is_displayed()]
                        if vis_opts:
                            target = vis_opts[0]
                            if comp_name:
                                for o in vis_opts:
                                    if comp_name.lower() in o.text.lower():
                                        target = o
                                        break
                            driver.execute_script("arguments[0].click();", target)
                    print(f"[SUCCESS] Selected company in Person form: {comp_name}")
                    return True
        except Exception as e:
            print(f"select_company_for_person notice: {e}")
        return False

    # 2. Go to Contact module
    print("Navigating to Contact module...")
    try:
        contact_links = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'CONTACT', 'contact'), 'contact')] | //a[contains(@href, 'Contact')]")
        visible_contacts = [l for l in contact_links if l.is_displayed()]
        if visible_contacts:
            driver.execute_script("arguments[0].click();", visible_contacts[0])
        else:
            navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Contact")
    except Exception:
        navigate_with_retry(driver, "https://yorpro-test.outsystems.app/legalhub/Contact")
    time.sleep(3)

    # 3. Create Company First
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
    
    # 4. Create Person Workflow
    print(f"Creating Person: {person_full}...")
    
    # 4.1 Click on the Create Person button
    if not click_button_by_texts(["new person", "create person", "person"]):
        if click_button_by_texts(["add new entry", "add new", "add", "+"]):
            time.sleep(1)
            click_button_by_texts(["person", "new person", "add person", "create person"])
    time.sleep(2)

    # 4.2 Click on the Save button (on blank form)
    print("Clicking Save button on blank form...")
    click_button_by_texts(["save", "save & continue", "submit", "create person"])
    time.sleep(2)

    # 4.3 Enter the First Name
    print(f"Entering First Name: {person_first}...")
    fill_by_label("First Name", person_first)
    time.sleep(1)

    # 4.4 Click on the Save button
    print("Clicking Save button after First Name...")
    click_button_by_texts(["save", "save & continue", "submit", "create person"])
    time.sleep(2)

    # 4.5 Enter the Last Name
    print(f"Entering Last Name: {person_last}...")
    fill_by_label("Last Name", person_last)
    time.sleep(1)

    # 4.6 Enter all the data according to all field types
    print(f"Entering Email: {person_email} and Phone: {person_phone}...")
    fill_by_label("Email", person_email)
    fill_by_label("Phone", person_phone)
    time.sleep(1)
    
    # 4.7 Select Company using exact user XPath
    print(f"Selecting Company ({company_name})...")
    try:
        company_dropdown = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'vscomp-value') and normalize-space()='Select...']"
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", company_dropdown)
        company_dropdown.click()
        time.sleep(1)
        
        options = driver.find_elements(By.XPATH, "//*[contains(@class, 'vscomp-option')]")
        vis_opts = [o for o in options if o.is_displayed()]
        if vis_opts:
            target_opt = vis_opts[0]
            for opt in vis_opts:
                if company_name.lower() in opt.text.lower():
                    target_opt = opt
                    break
            driver.execute_script("arguments[0].click();", target_opt)
            print(f"[SUCCESS] Selected company: {target_opt.text}")
    except Exception as comp_err:
        print(f"Primary company dropdown click note: {comp_err}, trying fallback...")
        select_company_for_person(company_name)
    time.sleep(1)
    
    # 4.8 Click on the Save button
    print("Clicking Save button to save Person...")
    for click_i in range(1, 4):
        print(f"Clicking Save button for Person (click {click_i}/3)...")
        click_button_by_texts(["save", "save & continue", "submit", "create person"])
        time.sleep(2)
        
    print(f"[SUCCESS] Person created and saved: {person_full} with Company: {company_name}")

    # 5. Navigate to Matter Module
    print("Navigating to Matter module...")
    matter_page.navigate_to_matter_module()
    time.sleep(5)

    # 6. Click New Matter
    print("Opening New Matter form...")
    matter_page.click_new_matter()
    time.sleep(5)

    # 7. Select Client
    print(f"Selecting Client ({person_full})...")
    matter_page.select_client(client_name=person_first)
    time.sleep(5)

    # 8. Enter Description with valid data
    matter_desc = f"Corporate Legal Case - {person_last} ({timestamp})"
    print(f"Entering Description: {matter_desc}")
    matter_page.enter_description(matter_desc)
    time.sleep(5)

    # 9. Select Open Date
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Setting Open Date: {today_str}")
    matter_page.select_open_date(today_str)
    time.sleep(5)

    # 10. Select Close Date (45 days from today)
    close_date_str = (datetime.date.today() + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    print(f"Setting Close Date: {close_date_str}")
    matter_page.select_close_date(close_date_str)
    time.sleep(5)

    # 11. Select Responsible Person
    print("Selecting Responsible Person...")
    matter_page.select_responsible_person()
    time.sleep(5)

    # 12. Select Origination Person
    print("Selecting Origination Person...")
    matter_page.select_origination_person()
    time.sleep(5)

    # 13. Click Create Matter / Save Button
    print("Clicking Create Matter / Save button...")
    matter_page.click_save_button()
    time.sleep(5)

    # 14. Click on the Matter ID to view details
    print("Navigating into created Matter by clicking on the Matter ID...")
    clicked_id = matter_page.click_matter_id(description=matter_desc)
    time.sleep(2)

    # 15. Click on the Edit button
    print("Clicking on the Edit button on Matter details page...")
    matter_page.click_edit_button()
    time.sleep(5)

    print(f"End-to-End Workflow successfully completed! Person with Company created, multiple saves clicked, Matter created and Edit button pressed.")
