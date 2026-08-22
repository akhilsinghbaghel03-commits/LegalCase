"""
conftest.py - Replaces Java BaseTest @BeforeSuite / @AfterSuite.

pytest session-scoped fixture: initialises the WebDriver once
before all tests and quits it after the entire suite finishes.

The `driver` fixture is injected into every test function that
declares it as a parameter — exactly mirroring Java's @BeforeClass
`this.driver = DriverFactory.getDriver()`.
"""

import datetime
import os

import pytest

from utils.config_reader import ConfigReader
from utils.driver_factory import DriverFactory
from utils.screenshot_utils import ScreenshotUtils


# ---------------------------------------------------------------------------
# Session-scoped driver fixture
# Replaces Java @BeforeSuite (init) and @AfterSuite (quit)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def driver():
    """
    Create a single WebDriver for the entire test session and
    yield it to every test. Tear it down after the session ends.

    Mirrors Java:
        @BeforeSuite  -> DriverFactory.initDriver(browser, headless)
        @AfterSuite   -> DriverFactory.quitDriver()
    """
    browser = ConfigReader.get_browser()
    headless = ConfigReader.is_headless()
    page_load_timeout = ConfigReader.get_page_load_timeout()

    # Init driver (Selenium 4.6+ auto-manages ChromeDriver/GeckoDriver)
    _driver = DriverFactory.init_driver(browser, headless)

    # Apply page load timeout
    from selenium.webdriver.common.timeouts import Timeouts
    _driver.set_page_load_timeout(page_load_timeout)
    _driver.maximize_window()

    yield _driver

    # Teardown — mirrors Java @AfterSuite
    DriverFactory.quit_driver()


# ---------------------------------------------------------------------------
# Failure diagnostics hook
# Replaces Java BaseTest.captureFailureDetails()
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test, if it failed, capture a screenshot and page source
    automatically. Mirrors Java captureFailureDetails().
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        _driver = item.funcargs.get("driver")
        if _driver:
            test_name = item.name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"FAILED_{test_name}_{timestamp}"

            print(f"\n========== FAILURE DIAGNOSTICS ==========")
            print(f"URL       : {_driver.current_url}")
            print(f"Title     : {_driver.title}")
            print(f"Timestamp : {datetime.datetime.now()}")

            ScreenshotUtils.capture(_driver, file_name)
            ScreenshotUtils.save_page_source(_driver, file_name)

            # Browser console logs (Chrome only)
            try:
                from selenium.webdriver.remote.webdriver import WebDriver
                logs = _driver.get_log("browser")
                print("\n----- Browser Logs -----")
                for entry in logs:
                    print(f"{entry['level']} : {entry['message']}")
            except Exception as exc:
                print(f"Browser log capture failed: {exc}")

from test.utils.helpers import get_driver

@pytest.fixture(scope="function")
def driver_setup():
    driver, wait = get_driver()
    yield driver, wait
    try:
        driver.quit()
    except Exception:
        pass


