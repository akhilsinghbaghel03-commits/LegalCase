"""
wait_utils.py - Replaces Java WaitUtils.

Provides explicit wait helpers using Selenium's WebDriverWait
and ExpectedConditions (EC).
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException


DEFAULT_TIMEOUT = 30


class WaitUtils:
    """
    Encapsulates Selenium explicit waits.
    Mirrors the Java WaitUtils class.
    """

    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout

    def wait_for_visible(
        self, element: WebElement, timeout: int = None
    ) -> WebElement:
        """
        Wait until the element is visible on the page.

        Args:
            element: The WebElement to wait for.
            timeout: Override default timeout (seconds).

        Returns:
            The visible WebElement.
        """
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of(element)
        )

    def wait_for_visible_by_locator(
        self, by, value: str, timeout: int = None
    ) -> WebElement:
        """
        Wait until an element located by (by, value) is visible.

        Args:
            by: selenium By strategy.
            value: Locator string.
            timeout: Override default timeout.

        Returns:
            The visible WebElement.
        """
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_for_clickable(
        self, element: WebElement, timeout: int = None
    ) -> WebElement:
        """
        Wait until the element is clickable.

        Args:
            element: The WebElement to wait for.
            timeout: Override default timeout (seconds).

        Returns:
            The clickable WebElement.
        """
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(element)
        )

    def wait_for_clickable_by_locator(
        self, by, value: str, timeout: int = None
    ) -> WebElement:
        """
        Wait until an element located by (by, value) is clickable.

        Args:
            by: selenium By strategy.
            value: Locator string.
            timeout: Override default timeout.

        Returns:
            The clickable WebElement.
        """
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable((by, value))
        )

    def wait_for_url_contains(
        self, url_fragment: str, timeout: int = None
    ) -> bool:
        """
        Wait until the current URL contains the given fragment.

        Replaces Java: waitUtils.waitForUrlContains("LegalHub")

        Args:
            url_fragment: Substring to look for in the URL.
            timeout: Override default timeout.

        Returns:
            True if URL matches within timeout, False otherwise.
        """
        t = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, t).until(
                EC.url_contains(url_fragment)
            )
        except TimeoutException:
            return False

    def wait_for_condition(self, condition_fn, timeout: int = None) -> bool:
        """
        Wait until an arbitrary condition function returns truthy.

        Replaces Java lambda-based wait.until() calls.

        Args:
            condition_fn: A callable(driver) -> truthy/falsy.
            timeout: Override default timeout.

        Returns:
            The truthy result, or False on timeout.
        """
        t = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, t).until(condition_fn)
        except TimeoutException:
            return False
