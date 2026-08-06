"""
login_page.py - Replaces Java LoginPage.

Handles all interactions with the LegalHub Login page:
URL launch, email/password entry, sign-in click, and
post-login state detection (OTP popup vs. login failure).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object for the LegalHub Login page.

    Locators are defined as class-level tuples (By strategy, value),
    replacing Java's @FindBy annotations and PageFactory.initElements.
    """

    # ------------------------------------------------------------------
    # Locators  (replaces Java @FindBy annotations)
    # ------------------------------------------------------------------
    _EMAIL_FIELD = (By.ID, "Input_UserEmail")
    _PASSWORD_FIELD = (By.ID, "Input_Password")
    _SIGN_IN_BUTTON = (
        By.XPATH,
        "//div[@class='display-flex sign-container']",
    )
    _OTP_INPUT = (By.XPATH, "//input[contains(@id,'OTP')]")
    _LOGIN_FAILED = (
        By.XPATH,
        "//*[contains(text(),'Login Failed') "
        "or contains(text(),'Invalid') "
        "or contains(text(),'incorrect') "
        "or contains(@class,'error') "
        "or contains(@class,'toast-error')]",
    )

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ------------------------------------------------------------------
    # Private helpers — resolve locators to live elements
    # ------------------------------------------------------------------

    def _email_field(self):
        return self.wait_utils.wait_for_visible_by_locator(*self._EMAIL_FIELD)

    def _password_field(self):
        return self.wait_utils.wait_for_visible_by_locator(*self._PASSWORD_FIELD)

    def _sign_in_button(self):
        return self.wait_utils.wait_for_clickable_by_locator(*self._SIGN_IN_BUTTON)

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def launch_application(self, url: str) -> None:
        """
        Navigate to the application URL.

        Replaces Java: launchApplication(String url)

        Args:
            url: The full URL to navigate to.

        Raises:
            RuntimeError: On navigation failure.
        """
        try:
            print(f"Launching URL: {url}")
            self.driver.get(url)
            print("Application launched successfully.")
        except TimeoutException as exc:
            raise RuntimeError(
                f"Application load timeout for URL: {url}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to launch application: {url}"
            ) from exc

    def enter_email(self, email: str) -> None:
        """
        Type email into the email field.

        Replaces Java: enterEmail(String email)
        """
        self.enter_text(self._email_field(), email)

    def enter_password(self, password: str) -> None:
        """
        Type password into the password field.

        Replaces Java: enterPassword(String password)
        """
        self.enter_text(self._password_field(), password)

    def clear_email(self) -> None:
        """
        Wait for the email field to be visible and clear it.

        Replaces Java: clearEmail()
        """
        field = self._email_field()
        self.wait_for_visible(field)
        field.clear()

    def clear_password(self) -> None:
        """
        Wait for the password field to be visible and clear it.

        Replaces Java: clearPassword()
        """
        field = self._password_field()
        self.wait_for_visible(field)
        field.clear()

    def click_sign_in_securely(self) -> None:
        """
        Click the Sign In button.

        Replaces Java: clickSignInSecurely()
        """
        self.click(self._sign_in_button())

    def is_otp_page_displayed(self) -> bool:
        """
        Check whether the OTP input fields are present on the page.

        Replaces Java: isOtpPageDisplayed()

        Returns:
            True if at least one OTP input field exists.
        """
        return len(self.driver.find_elements(*self._OTP_INPUT)) > 0

    def is_login_failed_displayed(self) -> bool:
        """
        Check whether a login-failure message or error toast is visible.

        Replaces Java: isLoginFailedDisplayed()

        Returns:
            True if a failure indicator is present on the page.
        """
        return len(self.driver.find_elements(*self._LOGIN_FAILED)) > 0

    def wait_for_otp_or_error(self, timeout: int = 45) -> bool:
        """
        Poll until either the OTP page, a login error, or an
        error toast appears — or the timeout expires.

        Replaces Java: waitForOtpOrError()

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            True if any of the expected conditions appeared.
            False if the timeout elapsed without a match.
        """
        def condition(driver):
            current_url = driver.getCurrentUrl() if hasattr(driver, "getCurrentUrl") else driver.current_url
            print(f"Polling URL: {current_url}")

            otp_count = len(
                driver.find_elements(By.XPATH, "//input[contains(@id,'OTP')]")
            )
            print(f"OTP Count: {otp_count}")

            otp_visible = otp_count > 0
            login_failed = len(
                driver.find_elements(
                    By.XPATH, "//*[contains(text(),'Login Failed')]"
                )
            ) > 0
            toast_error = len(
                driver.find_elements(
                    By.XPATH,
                    "//*[contains(@class,'error') or contains(@class,'toast')]",
                )
            ) > 0

            return otp_visible or login_failed or toast_error

        return self.wait_utils.wait_for_condition(condition, timeout=timeout)
