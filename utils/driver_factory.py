"""
driver_factory.py - Replaces Java DriverFactory.

Manages WebDriver lifecycle using a module-level dict keyed by
thread ID — mirrors Java's ThreadLocal<WebDriver> pattern.

Selenium 4.6+ includes selenium-manager which automatically
downloads the correct ChromeDriver / GeckoDriver, so no
WebDriverManager dependency is required.
"""

import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


_drivers: dict[int, WebDriver] = {}
_lock = threading.Lock()


class DriverFactory:
    """
    Creates, stores, and tears down WebDriver instances.

    Usage (mirrors Java):
        DriverFactory.init_driver("chrome", headless=False)
        driver = DriverFactory.get_driver()
        DriverFactory.quit_driver()
    """

    @staticmethod
    def init_driver(browser: str = "chrome", headless: bool = False) -> WebDriver:
        """
        Initialise a WebDriver for the given browser and store it.

        Args:
            browser: 'chrome' or 'firefox' (case-insensitive).
            headless: Run browser without a visible window.

        Returns:
            The newly created WebDriver instance.

        Raises:
            ValueError: If an unsupported browser name is provided.
        """
        thread_id = threading.get_ident()
        browser = browser.lower().strip()

        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            # Suppress "Chrome is being controlled" bar
            options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            options.add_experimental_option(
                "useAutomationExtension", False
            )
            driver = webdriver.Chrome(options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

        else:
            raise ValueError(
                f"Unsupported browser: '{browser}'. Use 'chrome' or 'firefox'."
            )

        with _lock:
            _drivers[thread_id] = driver

        print(f"[DriverFactory] Initialized {browser} driver (headless={headless})")
        return driver

    @staticmethod
    def get_driver() -> WebDriver:
        """
        Retrieve the WebDriver for the current thread.

        Returns:
            The active WebDriver instance.

        Raises:
            RuntimeError: If no driver has been initialised for this thread.
        """
        thread_id = threading.get_ident()
        driver = _drivers.get(thread_id)
        if driver is None:
            raise RuntimeError(
                "No WebDriver found for the current thread. "
                "Call DriverFactory.init_driver() first."
            )
        return driver

    @staticmethod
    def quit_driver():
        """
        Quit and remove the WebDriver for the current thread.
        Mirrors Java DriverFactory.quitDriver().
        """
        thread_id = threading.get_ident()
        with _lock:
            driver = _drivers.pop(thread_id, None)
        if driver:
            try:
                driver.quit()
                print("[DriverFactory] Driver quit successfully.")
            except Exception as exc:
                print(f"[DriverFactory] Driver quit error: {exc}")
