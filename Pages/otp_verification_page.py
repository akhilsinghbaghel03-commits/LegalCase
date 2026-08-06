"""
otp_verification_page.py - Replaces Java OtpVerificationPage.

Handles all interactions on the OTP Verification page:
waiting for OTP fields, entering the OTP digit-by-digit,
and clicking the Verify button.
"""

from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class OtpVerificationPage(BasePage):
    """
    Page Object for the OTP Verification page.

    Replaces Java OtpVerificationPage — locators are (By, value)
    tuples instead of @FindBy annotations.
    """

    # ------------------------------------------------------------------
    # Locators  (replaces Java @FindBy annotations)
    # ------------------------------------------------------------------
    _OTP_HEADING = (By.XPATH, "//span[normalize-space()='OTP Verification']")
    _OTP_FIELDS_LOCATOR = (By.XPATH, "//input[contains(@id,'OTP')]")
    _VERIFY_BUTTON = (By.XPATH, "//button[normalize-space()='Verify']")
    _ERROR_LOCATOR = (
        By.XPATH,
        "//*[contains(@class,'error') or contains(@class,'toast-error')]",
    )

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_otp_fields(self) -> List[WebElement]:
        """Return the current list of OTP input elements."""
        return self.driver.find_elements(*self._OTP_FIELDS_LOCATOR)

    def _verify_button(self) -> WebElement:
        return self.wait_utils.wait_for_clickable_by_locator(*self._VERIFY_BUTTON)

    def _otp_heading(self) -> WebElement:
        return self.wait_utils.wait_for_visible_by_locator(*self._OTP_HEADING)

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def is_otp_page_displayed(self, timeout: int = 45) -> bool:
        """
        Poll until the OTP inputs are visible or an application error
        is detected.

        Replaces Java: isOtpPageDisplayed() with WebDriverWait lambda.

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            True if OTP fields appear within the timeout.

        Raises:
            RuntimeError: If an application error toast is detected.
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                self._otp_or_error_condition
            )
        except TimeoutException:
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page Title: {self.driver.title}")
            print(
                f"OTP Fields Found: "
                f"{len(self.driver.find_elements(*self._OTP_FIELDS_LOCATOR))}"
            )
            print("OTP popup did not appear within 45 seconds.")
            return False

    @staticmethod
    def _otp_or_error_condition(driver: WebDriver) -> bool:
        """
        Custom ExpectedCondition: return True when OTP inputs are visible.
        Raise RuntimeError if an error element is detected first.
        """
        error_elements = driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'error') or contains(@class,'toast-error')]",
        )
        if error_elements:
            error_text = error_elements[0].text
            raise RuntimeError(f"Application error detected: {error_text}")

        otp_elements = driver.find_elements(
            By.XPATH, "//input[contains(@id,'OTP')]"
        )
        return len(otp_elements) > 0

    def get_otp_heading_text(self) -> str:
        """
        Return the heading text of the OTP page.

        Replaces Java: getOtpHeadingText()
        """
        heading = self._otp_heading()
        self.wait_for_visible(heading)
        return heading.text.strip()

    def enter_otp(self, otp: str) -> None:
        """
        Enter the OTP one digit per input field.

        Replaces Java: enterOtp(String otp)

        Args:
            otp: The OTP string retrieved from email.

        Raises:
            RuntimeError: If OTP is empty or fields are insufficient.
        """
        if not otp or not otp.strip():
            raise RuntimeError("OTP is null or empty")

        otp = otp.strip()
        otp_fields = self._get_otp_fields()

        if not otp_fields:
            raise RuntimeError("No OTP fields found on page")

        if len(otp_fields) < len(otp):
            raise RuntimeError(
                f"OTP field count mismatch. Found {len(otp_fields)} fields "
                f"but OTP length is {len(otp)}"
            )

        print(f"Entering OTP: {otp}")

        for i, char in enumerate(otp):
            field = otp_fields[i]
            self.wait_for_visible(field)
            field.clear()
            field.send_keys(char)

    def click_verify(self) -> None:
        """
        Click the Verify button.

        Replaces Java: clickVerify()
        """
        btn = self._verify_button()
        self.wait_for_clickable(btn)
        btn.click()

    def verify_otp(self, otp: str) -> None:
        """
        Enter OTP and click Verify in one step.

        Replaces Java: verifyOtp(String otp)

        Args:
            otp: The OTP string to submit.
        """
        self.enter_otp(otp)
        self.click_verify()

    def get_otp_field_count(self) -> int:
        """
        Return the number of OTP input fields currently on the page.

        Replaces Java: getOtpFieldCount()
        """
        return len(self.driver.find_elements(*self._OTP_FIELDS_LOCATOR))
