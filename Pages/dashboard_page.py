"""
dashboard_page.py - Replaces Java DashboardPage.

Waits for the LegalHub dashboard to load after successful
OTP verification by polling the current URL for the expected
path fragment.
"""

from selenium.webdriver.remote.webdriver import WebDriver

from Pages.base_page import BasePage
from utils.config_reader import ConfigReader


class DashboardPage(BasePage):
    """
    Page Object for the LegalHub Dashboard.

    Replaces Java DashboardPage — uses wait_utils.wait_for_url_contains
    instead of a custom Java WaitUtils helper.
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def wait_for_dashboard_to_load(self, timeout: int = None) -> bool:
        """
        Wait until the browser URL contains 'LegalHub', indicating
        that the dashboard has loaded successfully.

        Replaces Java: waitForDashboardToLoad()

        Args:
            timeout: Seconds to wait (defaults to config dashboard_wait).

        Returns:
            True if the dashboard URL is reached within the timeout.
            False otherwise.
        """
        print("Waiting for Dashboard to load...")

        t = timeout or ConfigReader.get_dashboard_wait()

        try:
            result = self.wait_utils.wait_for_url_contains("LegalHub", timeout=t)
        except Exception as exc:
            print("========== DASHBOARD LOAD FAILED ==========")
            print(f"URL  : {self.driver.current_url}")
            print(f"Title: {self.driver.title}")
            print("==========================================")
            print(f"Error: {exc}")
            return False

        if not result:
            print("========== DASHBOARD LOAD FAILED ==========")
            print(f"URL  : {self.driver.current_url}")
            print(f"Title: {self.driver.title}")
            print("==========================================")

        return result
