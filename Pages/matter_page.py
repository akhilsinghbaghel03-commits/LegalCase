"""
matter_page.py - Page Object for the Matter module.
Handles creation, form interaction (Client, Description, Open/Close Dates, Responsible/Origination Person),
saving, and navigating to Matter details by clicking Matter ID.
Includes robust error handling and 5-second delays between actions.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Pages.base_page import BasePage


class MatterPage(BasePage):
    """
    Page Object for the Matter module with 5-second delays between actions.
    """

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    _MATTER_MODULE_LINK = (By.XPATH, "//*[contains(translate(text(), 'MATTER', 'matter'), 'matter')] | //a[contains(@href, 'Matter') or contains(@href, 'matter')]")
    _NEW_MATTER_BUTTON = (By.XPATH, "//button[contains(., 'New Matter') or contains(., 'Matter') or contains(., 'Add Matter')] | //*[contains(text(), 'New Matter')] | //button[contains(., '+')]")
    _SAVE_BUTTON = (By.XPATH, "//button[contains(., 'Create Matter') or contains(., 'Save') or contains(., 'Submit') or contains(., 'Create') or contains(., 'Save & Continue')] | //a[contains(., 'Create Matter') or contains(., 'Save')] | //button[@type='submit']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    
    def navigate_to_matter_module(self) -> None:
        """Navigate to the Matter module and wait 5 seconds."""
        try:
            links = self.driver.find_elements(*self._MATTER_MODULE_LINK)
            visible_links = [l for l in links if l.is_displayed()]
            if visible_links:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", visible_links[0])
            else:
                self.driver.get("https://yorpro-test.outsystems.app/legalhub/Matter")
        except Exception:
            self.driver.get("https://yorpro-test.outsystems.app/legalhub/Matter")
        time.sleep(5)

    def click_new_matter(self) -> None:
        """Click the New Matter button and wait 5 seconds."""
        try:
            buttons = self.driver.find_elements(*self._NEW_MATTER_BUTTON)
            clicked = False
            for btn in buttons:
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", btn)
                    clicked = True
                    break
            if not clicked:
                add_btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'Add') or contains(., 'New')]")
                for btn in add_btns:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", btn)
                        break
        except Exception as e:
            print(f"click_new_matter notice: {e}")
        time.sleep(5)

    def select_client(self, client_name: str = None) -> None:
        """Select a client from the Client dropdown / vscomp and wait 5 seconds."""
        try:
            client_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(translate(text(), 'CLIENT', 'client'), 'client')]/following::div[contains(@class, 'vscomp-toggle-button') or contains(@class, 'vscomp-wrapper')][1] | "
                "//div[@class='vscomp-value' and @data-tooltip=\"What's the contact name\"] | "
                "//div[contains(@class, 'vscomp-toggle-button')]"
            )
            if client_elements and client_elements[0].is_displayed():
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", client_elements[0])
                time.sleep(1)
                options = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'vscomp-option')]")
                visible_opts = [o for o in options if o.is_displayed()]
                if visible_opts:
                    target_opt = visible_opts[1] if len(visible_opts) > 1 else visible_opts[0]
                    if client_name:
                        for opt in visible_opts:
                            if client_name.lower() in opt.text.lower():
                                target_opt = opt
                                break
                    self.driver.execute_script("arguments[0].click();", target_opt)
            else:
                dropdown = self.driver.find_element(By.XPATH, "//*[contains(translate(text(), 'CLIENT', 'client'), 'client')]/following::select[1] | //*[contains(translate(text(), 'CLIENT', 'client'), 'client')]/following::input[1]")
                self.driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(1)
                dropdown.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        except Exception as e:
            print(f"select_client notice: {e}")
        time.sleep(5)

    def enter_description(self, description: str) -> None:
        """Enter description into the Matter Description field and wait 5 seconds."""
        try:
            desc_fields = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(translate(text(), 'DESCRIPTION', 'description'), 'description')]/following::textarea[1] | "
                "//*[contains(translate(text(), 'DESCRIPTION', 'description'), 'description')]/following::input[1] | "
                "//textarea[contains(@placeholder, 'description') or contains(@id, 'Description')] | "
                "//textarea"
            )
            for el in desc_fields:
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    el.clear()
                    el.send_keys(description)
                    self.driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, el, description)
                    break
        except Exception as e:
            print(f"enter_description notice: {e}")
        time.sleep(5)

    def select_open_date(self, date_str: str = None) -> None:
        """Select/enter the Open Date and wait 5 seconds."""
        if not date_str:
            import datetime
            date_str = datetime.date.today().strftime("%Y-%m-%d")
        try:
            date_inputs = self.driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'OPEN DATE', 'open date'), 'open date') or contains(translate(text(), 'OPENDATE', 'opendate'), 'opendate') or contains(translate(text(), 'START DATE', 'start date'), 'start date')]/following::input[1] | "
                "//input[@type='date' or contains(@id, 'OpenDate') or contains(@id, 'StartDate') or contains(@placeholder, 'Open Date')]"
            )
            for inp in date_inputs:
                if inp.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                    self.driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, inp, date_str)
                    break
        except Exception as e:
            print(f"select_open_date notice: {e}")
        time.sleep(5)

    def select_close_date(self, date_str: str = None) -> None:
        """Select/enter the Close Date and wait 5 seconds."""
        if not date_str:
            import datetime
            date_str = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        try:
            date_inputs = self.driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'CLOSE DATE', 'close date'), 'close date') or contains(translate(text(), 'CLOSEDATE', 'closedate'), 'closedate') or contains(translate(text(), 'DUE DATE', 'due date'), 'due date')]/following::input[1] | "
                "//input[contains(@id, 'CloseDate') or contains(@id, 'DueDate') or contains(@placeholder, 'Close Date')]"
            )
            for inp in date_inputs:
                if inp.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                    self.driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, inp, date_str)
                    break
        except Exception as e:
            print(f"select_close_date notice: {e}")
        time.sleep(5)

    def select_responsible_person(self, person_name: str = None) -> None:
        """Select Responsible Attorney / Person and wait 5 seconds."""
        try:
            resp_elements = self.driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'RESPONSIBLE', 'responsible'), 'responsible')]/following::div[contains(@class, 'vscomp-toggle-button') or contains(@class, 'vscomp-wrapper')][1] | "
                "//*[contains(translate(text(), 'RESPONSIBLE', 'responsible'), 'responsible')]/following::select[1] | "
                "//*[contains(translate(text(), 'RESPONSIBLE', 'responsible'), 'responsible')]/following::input[1]"
            )
            for el in resp_elements:
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
                    time.sleep(1)
                    options = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'vscomp-option')]")
                    visible_opts = [o for o in options if o.is_displayed()]
                    if visible_opts:
                        self.driver.execute_script("arguments[0].click();", visible_opts[0])
                    else:
                        el.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
                    break
        except Exception as e:
            print(f"select_responsible_person notice: {e}")
        time.sleep(5)

    def select_origination_person(self, person_name: str = None) -> None:
        """Select Origination Attorney / Person and wait 5 seconds."""
        try:
            orig_elements = self.driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'ORIGINATION', 'origination'), 'origination') or contains(translate(text(), 'ORIGINATING', 'originating'), 'originating')]/following::div[contains(@class, 'vscomp-toggle-button') or contains(@class, 'vscomp-wrapper')][1] | "
                "//*[contains(translate(text(), 'ORIGINATION', 'origination'), 'origination') or contains(translate(text(), 'ORIGINATING', 'originating'), 'originating')]/following::select[1] | "
                "//*[contains(translate(text(), 'ORIGINATION', 'origination'), 'origination') or contains(translate(text(), 'ORIGINATING', 'originating'), 'originating')]/following::input[1]"
            )
            for el in orig_elements:
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", el)
                    time.sleep(1)
                    options = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'vscomp-option')]")
                    visible_opts = [o for o in options if o.is_displayed()]
                    if visible_opts:
                        self.driver.execute_script("arguments[0].click();", visible_opts[0])
                    else:
                        el.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
                    break
        except Exception as e:
            print(f"select_origination_person notice: {e}")
        time.sleep(5)

    def click_save_button(self) -> None:
        """Click the Save / Create Matter button and wait 5 seconds."""
        try:
            buttons = self.driver.find_elements(*self._SAVE_BUTTON)
            for btn in buttons:
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", btn)
                    break
        except Exception as e:
            print(f"click_save_button notice: {e}")
        time.sleep(5)

    def click_matter_id(self, matter_id: str = None, description: str = None) -> bool:
        """
        Click on the Matter ID (or the link/row corresponding to the newly created matter)
        to open the Matter details page, and wait 2 seconds.
        """
        time.sleep(1)
        try:
            if description:
                row_links = self.driver.find_elements(
                    By.XPATH,
                    f"//tr[td[contains(., '{description}')]]//a | "
                    f"//tr[td[contains(., '{description}')]]//td[1]//a | "
                    f"//tr[td[contains(., '{description}')]]//td[1]"
                )
                for link in row_links:
                    if link.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", link)
                        time.sleep(2)
                        return True

            if matter_id:
                id_links = self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{matter_id}')] | //*[contains(text(), '{matter_id}')]")
                for link in id_links:
                    if link.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", link)
                        time.sleep(2)
                        return True

            table_id_links = self.driver.find_elements(
                By.XPATH,
                "//table//tbody//tr[1]//td[1]//a | "
                "//table//tbody//tr[1]//a | "
                "//div[contains(@class, 'table-row')][1]//a"
            )
            for link in table_id_links:
                if link.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", link)
                    time.sleep(2)
                    return True
        except Exception as e:
            print(f"click_matter_id notice: {e}")
        time.sleep(2)
        return False

    def click_edit_button(self) -> bool:
        """
        Click on the Edit button on the Matter details page, and wait 5 seconds.
        """
        time.sleep(2)
        try:
            edit_btns = self.driver.find_elements(
                By.XPATH,
                "//button[contains(translate(., 'EDIT', 'edit'), 'edit')] | "
                "//a[contains(translate(., 'EDIT', 'edit'), 'edit')] | "
                "//*[contains(@class, 'edit-btn') or contains(@class, 'btn-edit') or contains(@id, 'Edit') or contains(@id, 'edit')]"
            )
            for btn in edit_btns:
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", btn)
                    print("[SUCCESS] Clicked on Matter Edit button.")
                    time.sleep(5)
                    return True
        except Exception as e:
            print(f"click_edit_button notice: {e}")
        time.sleep(5)
        return False
