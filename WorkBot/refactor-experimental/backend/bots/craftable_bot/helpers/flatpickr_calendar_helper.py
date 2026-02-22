from __future__ import annotations

import calendar
import time
from dataclasses import dataclass
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass(frozen=True)
class FlatpickrSelectors:
    # Your input looks like: <input id="ember2423" ... readonly ...>
    input_css: str = "input.flatpickr-input[data-input]"
    calendar_css: str = "div.flatpickr-calendar.open"

    # Header pieces (month name and year input)
    month_name_css: str = "div.flatpickr-month .flatpickr-current-month .cur-month"
    year_input_css: str = "div.flatpickr-month .flatpickr-current-month input.cur-year"

    # Prev/Next controls
    prev_css: str = "span.flatpickr-prev-month"
    next_css: str = "span.flatpickr-next-month"

    # Day cells (we'll target by aria-label)
    day_css: str = "span.flatpickr-day"


class FlatpickrController:
    def __init__(self, driver: webdriver.Remote, selectors: FlatpickrSelectors = FlatpickrSelectors(), timeout: int = 15):
        self.driver = driver
        self.sel = selectors
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        """
        Ensure the flatpickr calendar is open.
        """
        # Click the input (readonly inputs are normal for flatpickr)
        inp = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.sel.input_css)))
        inp.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.sel.calendar_css)))

    def _get_displayed_month_year(self) -> tuple[int, int]:
        """
        Returns (year, month) currently shown by the widget.
        """
        cal_el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.sel.calendar_css)))

        month_name = cal_el.find_element(By.CSS_SELECTOR, self.sel.month_name_css).text.strip()
        # flatpickr month text often includes a trailing space e.g. "September "
        month_name = month_name.strip()

        year_str = cal_el.find_element(By.CSS_SELECTOR, self.sel.year_input_css).get_attribute("value").strip()
        year = int(year_str)

        # Map "September" -> 9
        month = list(calendar.month_name).index(month_name)  # month_name list has '' at index 0
        if month == 0:
            raise ValueError(f"Could not parse month name from header: {month_name!r}")

        return year, month

    def _click_prev(self) -> None:
        cal_el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.sel.calendar_css)))
        btn = cal_el.find_element(By.CSS_SELECTOR, self.sel.prev_css)
        self.driver.execute_script("arguments[0].click();", btn)

    def _click_next(self) -> None:
        cal_el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.sel.calendar_css)))
        btn = cal_el.find_element(By.CSS_SELECTOR, self.sel.next_css)
        self.driver.execute_script("arguments[0].click();", btn)

    def goto_month(self, target: date, max_steps: int = 240) -> None:
        """
        Navigate month-by-month until the displayed month/year matches target.
        max_steps guards against infinite loops.
        """
        target_year, target_month = target.year, target.month

        for _ in range(max_steps):
            year, month = self._get_displayed_month_year()
            if (year, month) == (target_year, target_month):
                return

            # Decide direction by comparing (year, month)
            if (year, month) < (target_year, target_month):
                self._click_next()
            else:
                self._click_prev()

            # Small wait for DOM update
            time.sleep(0.05)

        raise TimeoutError(f"Could not navigate to {target_year}-{target_month:02d} within {max_steps} steps")

    @staticmethod
    def _aria_label_for(d: date) -> str:
        # Your HTML uses: aria-label="September 26, 2025"
        return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")

    def pick_date(self, d: date) -> None:
        """
        Open calendar, navigate to month, click day by aria-label.
        """
        self.open()
        self.goto_month(d)

        label = self._aria_label_for(d)
        cal_el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.sel.calendar_css)))

        # Find the exact day cell by aria-label
        day = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'{self.sel.day_css}[aria-label="{label}"]')
            )
        )

        # Use JS click to avoid overlay / interception issues
        self.driver.execute_script("arguments[0].click();", day)


def parse_date(s: str) -> date:
    """
    Accepts:
      - YYYY-MM-DD
      - YYYY/MM/DD
      - MM/DD/YYYY
    """
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized date format: {s!r}")

