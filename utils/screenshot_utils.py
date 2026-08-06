"""
screenshot_utils.py - Replaces Java ScreenshotUtils.

Captures screenshots and saves them to the target/ directory.
"""

import os
import datetime
from selenium.webdriver.remote.webdriver import WebDriver


class ScreenshotUtils:
    """
    Utility class for capturing screenshots during test failures.
    Mirrors Java ScreenshotUtils.capture().
    """

    TARGET_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "target"
    )

    @classmethod
    def capture(cls, driver: WebDriver, file_name: str) -> str:
        """
        Capture a screenshot and save to target/<file_name>.png.

        Args:
            driver: Active WebDriver instance.
            file_name: Base name for the screenshot file (no extension).

        Returns:
            Absolute path of the saved screenshot.
        """
        os.makedirs(cls.TARGET_DIR, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{file_name}_{timestamp}.png"
        file_path = os.path.join(cls.TARGET_DIR, safe_name)

        try:
            driver.save_screenshot(file_path)
            print(f"Screenshot saved: {file_path}")
        except Exception as exc:
            print(f"Screenshot capture failed: {exc}")

        return file_path

    @classmethod
    def save_page_source(cls, driver: WebDriver, file_name: str) -> str:
        """
        Save the current page HTML source to target/<file_name>.html.

        Replaces Java: Files.write(Paths.get("target/" + fileName + ".html"), ...)

        Args:
            driver: Active WebDriver instance.
            file_name: Base name for the HTML file (no extension).

        Returns:
            Absolute path of the saved HTML file.
        """
        os.makedirs(cls.TARGET_DIR, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{file_name}_{timestamp}.html"
        file_path = os.path.join(cls.TARGET_DIR, safe_name)

        try:
            html = driver.page_source
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Page source saved: {file_path}")
        except Exception as exc:
            print(f"Page source save failed: {exc}")

        return file_path
