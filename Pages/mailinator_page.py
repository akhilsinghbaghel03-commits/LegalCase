"""
mailinator_page.py - Replaces Java MailinatorPage.

Handles all interactions with the Mailinator public inbox:
navigation, inbox search, email opening, iframe switching,
and OTP extraction from the email body.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Pages.base_page import BasePage


class MailinatorPage(BasePage):
    """
    Page Object for www.mailinator.com.

    Replaces Java MailinatorPage — uses (By, value) locator tuples
    instead of @FindBy annotations.
    """

    # ------------------------------------------------------------------
    # Locators  (replaces Java @FindBy annotations)
    # ------------------------------------------------------------------
    _SEARCH_BOX = (By.ID, "search")
    _GO_BUTTON = (
        By.XPATH,
        "//button[contains(text(), 'GO') "
        "or @value='Search for public inbox for free']",
    )
    _LATEST_OTP_EMAIL = (
        By.XPATH,
        "//td[contains(text(), 'OTP Verification Code')]",
    )
    _EMAIL_IFRAME = (By.ID, "html_msg_body")
    _EMAIL_BODY = (By.TAG_NAME, "body")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ------------------------------------------------------------------
    # Private helpers — resolve locators to live elements
    # ------------------------------------------------------------------

    def _search_box(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._SEARCH_BOX)

    def _go_button(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._GO_BUTTON)

    def _latest_otp_email(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._LATEST_OTP_EMAIL)

    def _email_iframe(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._EMAIL_IFRAME)

    def _email_body(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._EMAIL_BODY)

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def navigate_to_mailinator(self) -> None:
        """
        Open the Mailinator homepage.

        Replaces Java: navigateToMailinator()
        """
        self.driver.get("https://www.mailinator.com/")

    def search_inbox(self, email: str) -> None:
        """
        Search for the given email address's public inbox.

        Replaces Java: searchInbox(String email)

        Args:
            email: Full email address; only the username part is used.
        """
        username = email.split("@")[0]
        self.enter_text(self._search_box(), username)
        self.click(self._go_button())

    def open_latest_email(self) -> None:
        """
        Click the most recent OTP Verification Code email in the inbox.

        Replaces Java: openLatestEmail()
        """
        self.click(self._latest_otp_email())

    def read_otp_from_email(self) -> str | None:
        """
        Switch into the email iframe, read the body text, switch back,
        and extract the OTP.

        Replaces Java: readOtpFromEmail()

        Returns:
            The OTP string, or None if extraction fails.
        """
        iframe = self._email_iframe()
        self.wait_for_visible(iframe)
        self.driver.switch_to.frame(iframe)

        body_text = self._email_body().text
        self.driver.switch_to.default_content()

        return self.extract_otp(body_text)
