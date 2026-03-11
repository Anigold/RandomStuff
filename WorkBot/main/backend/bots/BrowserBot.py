# backend/bots/base/browser_bot.py
from __future__ import annotations
import time
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from backend.infra.logger import Logger
from typing import Any

@Logger.attach_logger
@dataclass
class BrowserBot:

    driver: Any
    default_timeout: int = 30

    def goto(self, url: str):
        self.logger.info(f"Navigating to {url}")
        self.driver.get(url)

    def wait_for(self, locator: tuple, condition: str = "clickable", timeout: int | None = None):
        """Wait until an element satisfies a Selenium condition."""
        timeout = timeout or self.default_timeout
        cond = {
            "clickable": EC.element_to_be_clickable(locator),
            "visible": EC.visibility_of_element_located(locator),
            "present": EC.presence_of_element_located(locator),
        }.get(condition)

        try:
            return WebDriverWait(self.driver, timeout).until(cond)
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for {locator} ({condition})")
            return None

    def find(self, by, value, many=False):
        try:
            return self.driver.find_elements(by, value) if many else self.driver.find_element(by, value)
        except Exception as e:
            self.logger.debug(f"Element not found: {value} ({e})")
            return [] if many else None

    def close(self):
        try:
            self.driver.close()
            self.logger.info("Closed browser session.")
        except Exception as e:
            self.logger.warning(f"Error closing session: {e}")

    def sleep(self, sec: int):
        time.sleep(sec)
