"""
matter_page.py - Page Object for the Matter module.
Handles creation and editing of matters.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Pages.base_page import BasePage


class MatterPage(BasePage):
    """
    Page Object for the Matter module.
    """

    # ------------------------------------------------------------------
    # Locators (Placeholder locators to be updated by the user)
    # ------------------------------------------------------------------
    _MATTER_MODULE_LINK = (By.XPATH, "//a[contains(text(), 'Matter')]")
    _NEW_MATTER_BUTTON = (By.XPATH, "//button[contains(text(), 'New Matter')]")
    
    _CLIENT_DROPDOWN = (By.ID, "ClientId")  # Update with actual ID or locator
    _DESCRIPTION_FIELD = (By.ID, "Description")  # Update with actual ID or locator
    _SAVE_BUTTON = (By.XPATH, "//button[contains(text(), 'Save')]")
    
    _SUCCESS_TOAST = (By.XPATH, "//*[contains(@class, 'toast-success') or contains(text(), 'successfully')]")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ------------------------------------------------------------------
    # Private helpers — resolve locators to live elements
    # ------------------------------------------------------------------
    
    def _matter_module_link(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._MATTER_MODULE_LINK)

    def _new_matter_button(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._NEW_MATTER_BUTTON)

    def _client_dropdown(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._CLIENT_DROPDOWN)

    def _description_field(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._DESCRIPTION_FIELD)
        
    def _save_button(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._SAVE_BUTTON)

    def _success_toast(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._SUCCESS_TOAST)

    def _get_edit_icon_for_matter(self, description: str) -> WebElement:
        """
        Dynamically locate the Edit icon for a specific matter in the table.
        Assuming the table row contains the description and an edit icon.
        """
        locator = (By.XPATH, f"//tr[td[contains(text(), '{description}')]]//button[contains(@class, 'edit') or @title='Edit']")
        return self.wait_utils.wait_for_clickable_by_locator(*locator)

    def _get_client_name_for_matter(self, description: str) -> str:
        """
        Dynamically read the client name from the row of the given matter description.
        Assuming the client name is in a td class 'client-name' or similar.
        """
        locator = (By.XPATH, f"//tr[td[contains(text(), '{description}')]]/td[contains(@class, 'client')]")
        element = self.wait_utils.wait_for_visible_by_locator(*locator)
        return element.text

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def navigate_to_matter_module(self) -> None:
        """Click the Matter module link."""
        self.click(self._matter_module_link())

    def click_new_matter(self) -> None:
        """Click the New Matter button."""
        self.click(self._new_matter_button())

    def create_matter(self, client_name: str, description: str) -> None:
        """
        Fill the matter creation form and save.
        """
        self.select_dropdown_by_visible_text(self._client_dropdown(), client_name)
        self.enter_text(self._description_field(), description)
        self.click(self._save_button())

    def verify_success_message(self) -> bool:
        """Check if success toast appears."""
        try:
            toast = self._success_toast()
            return toast.is_displayed()
        except Exception:
            return False

    def click_edit_matter(self, description: str) -> None:
        """
        Click the edit icon for the matter matching the description.
        """
        edit_icon = self._get_edit_icon_for_matter(description)
        self.click(edit_icon)

    def edit_matter_client(self, new_client_name: str) -> None:
        """
        Change the client in the edit form and save.
        """
        self.select_dropdown_by_visible_text(self._client_dropdown(), new_client_name)
        self.click(self._save_button())

    def verify_client_updated(self, description: str, expected_client_name: str) -> bool:
        """
        Verify that the client name for the specific matter matches the expected one.
        """
        actual_client = self._get_client_name_for_matter(description)
        return actual_client.strip() == expected_client_name.strip()
