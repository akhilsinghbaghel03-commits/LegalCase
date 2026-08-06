"""
base_page.py - Replaces Java BasePage.

All page objects inherit from BasePage, which provides common
Selenium helper methods: wait, click, enter text, get text,
tab management, and OTP extraction.
"""

import re
from typing import List

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from utils.wait_utils import WaitUtils


class BasePage:
    """
    Base class for all Page Object classes.

    Mirrors Java BasePage — provides shared Selenium helpers
    so individual page classes stay focused on page-specific logic.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait_utils = WaitUtils(driver)

    # ------------------------------------------------------------------
    # Wait helpers
    # ------------------------------------------------------------------

    def wait_for_visible(
        self, element: WebElement, timeout: int = None
    ) -> WebElement:
        """Wait until element is visible and return it."""
        return self.wait_utils.wait_for_visible(element, timeout)

    def wait_for_clickable(
        self, element: WebElement, timeout: int = None
    ) -> WebElement:
        """Wait until element is clickable and return it."""
        return self.wait_utils.wait_for_clickable(element, timeout)

    # ------------------------------------------------------------------
    # Interaction helpers
    # ------------------------------------------------------------------

    def enter_text(self, element: WebElement, text: str) -> None:
        """
        Clear the element and type text into it.

        Replaces Java: enterText(WebElement, String)
        """
        self.wait_for_visible(element)
        element.clear()
        element.send_keys(text)

    def click(self, element: WebElement) -> None:
        """
        Wait for element to be clickable, then click it.

        Replaces Java: click(WebElement)
        """
        self.wait_for_clickable(element)
        element.click()

    def get_text(self, element: WebElement) -> str:
        """
        Wait for element to be visible and return its text.

        Replaces Java: getText(WebElement)
        """
        self.wait_for_visible(element)
        return element.text

    def select_dropdown_by_visible_text(self, element: WebElement, text: str) -> None:
        """
        Wait for a select element to be visible, then select by visible text.
        """
        self.wait_for_visible(element)
        select = Select(element)
        select.select_by_visible_text(text)

    def select_dropdown_by_value(self, element: WebElement, value: str) -> None:
        """
        Wait for a select element to be visible, then select by value attribute.
        """
        self.wait_for_visible(element)
        select = Select(element)
        select.select_by_value(value)

    # ------------------------------------------------------------------
    # Tab / window management
    # ------------------------------------------------------------------

    def switch_to_new_tab(self) -> None:
        """
        Open a new browser tab and switch to it.

        Replaces Java: driver.switchTo().newWindow(WindowType.TAB)
        """
        self.driver.switch_to.new_window("tab")

    def switch_to_tab(self, index: int) -> None:
        """
        Switch focus to the browser tab at position ``index``.

        Replaces Java: switchToTab(int index)

        Args:
            index: Zero-based tab index.
        """
        handles: List[str] = list(self.driver.window_handles)
        if index < len(handles):
            self.driver.switch_to.window(handles[index])
        else:
            raise IndexError(
                f"Tab index {index} out of range. "
                f"Only {len(handles)} tab(s) are open."
            )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def extract_otp(self, text: str) -> str | None:
        """
        Extract the first 4-8 digit numeric sequence from text.

        Replaces Java: extractOtp(String text) using Pattern/Matcher.

        Args:
            text: Raw string (e.g. email body).

        Returns:
            The OTP string, or None if no match found.
        """
        pattern = re.compile(r"\b\d{4,8}\b")
        match = pattern.search(text)
        return match.group() if match else None
