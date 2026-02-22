from __future__ import annotations

import calendar as calmod
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------
# Helpers
# ----------------------------

def parse_date(s: str) -> date:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized date format: {s!r}")


def aria_label_for(d: date) -> str:
    # Flatpickr uses e.g. "September 26, 2025"
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def month_num(month_name: str) -> int:
    name = month_name.strip()
    m = list(calmod.month_name).index(name)  # '' at index 0
    if m == 0:
        raise ValueError(f"Could not parse month name: {month_name!r}")
    return m


# ----------------------------
# Selectors
# ----------------------------

@dataclass(frozen=True)
class FP:
    # Each datepicker appears inside a wrapper
    wrapper_css: str = "div.flatpickr-wrapper"

    # The input inside wrapper (readonly is normal)
    input_css: str = "input.flatpickr-input[data-input]"

    # Calendar container for THAT wrapper
    calendar_css: str = "div.flatpickr-calendar"

    # Header elements inside the calendar
    month_name_css: str = ".flatpickr-current-month .cur-month"
    year_input_css: str = ".flatpickr-current-month input.cur-year"

    # Prev/next
    prev_css: str = ".flatpickr-prev-month"
    next_css: str = ".flatpickr-next-month"

    # Day cells
    day_css: str = "span.flatpickr-day"

    # Optional: open-state class used by flatpickr
    open_class: str = "open"


WidgetRef = Union[int, str, WebElement]
# int -> index into discovered widgets
# str -> label text ("From Date", "To Date") OR CSS selector for wrapper (see resolve)
# WebElement -> wrapper element


class FlatpickrWidgets:
    """
    General controller for N independent flatpickr widgets on a page, where each widget has:
      <label> ... </label>
      <div class="flatpickr-wrapper">
          <input class="flatpickr-input" ...>
          <div class="flatpickr-calendar"> ... </div>
      </div>

    Works by scoping all queries to the chosen wrapper, so calendars never collide.
    """

    def __init__(self, driver: webdriver.Remote, selectors: FP = FP(), timeout: int = 15):
        self.driver = driver
        self.fp = selectors
        self.wait = WebDriverWait(driver, timeout)

    # ----------------------------
    # Discovery / indexing
    # ----------------------------

    def list_widgets(self) -> List[WebElement]:
        """Return all flatpickr wrappers found on the page."""
        return self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.fp.wrapper_css)))

    def map_widgets_by_label(self) -> Dict[str, WebElement]:
        """
        Attempts to map widgets by the nearest preceding label text within the same '.mb-3 ...' column.
        In your HTML, the label is a sibling of the wrapper inside the same column div.

        Returns dict like:
          {"From Date": <wrapper_el>, "To Date": <wrapper_el>, ...}
        """
        widgets = self.list_widgets()
        mapping: Dict[str, WebElement] = {}

        for w in widgets:
            label = self._nearest_label_text(w)
            if label:
                mapping[label] = w

        return mapping

    def resolve_widget(self, ref: WidgetRef) -> WebElement:
        """
        Resolve a widget wrapper by:
          - WebElement: return as-is
          - int: index in list_widgets()
          - str: if matches a label text, return that widget
                 else treat as CSS selector for the wrapper
        """
        if isinstance(ref, WebElement):
            return ref

        if isinstance(ref, int):
            widgets = self.list_widgets()
            if ref < 0 or ref >= len(widgets):
                raise IndexError(f"Widget index {ref} out of range (found {len(widgets)})")
            return widgets[ref]

        if isinstance(ref, str):
            # First: try as label text
            by_label = self.map_widgets_by_label()
            if ref in by_label:
                return by_label[ref]

            # Fallback: treat as wrapper CSS selector
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ref)))

        raise TypeError(f"Unsupported widget ref type: {type(ref)!r}")

    # ----------------------------
    # Public API
    # ----------------------------

    def pick_date(self, widget: WidgetRef, target: date) -> None:
        """
        Open a specific widget's calendar and click the target date.
        """
        w = self.resolve_widget(widget)
        self._open_widget(w)

        cal = self._calendar(w)  # scoped
        self._goto_month(cal, target)
        self._click_day(cal, target)

    def get_value(self, widget: WidgetRef) -> str:
        w = self.resolve_widget(widget)
        inp = w.find_element(By.CSS_SELECTOR, self.fp.input_css)
        return inp.get_attribute("value") or ""

    # ----------------------------
    # Internals (scoped to wrapper/calendar)
    # ----------------------------

    def _nearest_label_text(self, wrapper: WebElement) -> Optional[str]:
        """
        Find the label text associated with this widget.
        Assumes DOM structure like:
          <div class="mb-3 ...">
              <label>From Date</label>
              <div ...><div class="flatpickr-wrapper">...</div></div>
          </div>
        """
        # Walk up to a "column" container then read its first <label>
        # This is intentionally flexible: match any ancestor with class containing 'mb-3'.
        script = r"""
            const wrapper = arguments[0];
            let node = wrapper;
            while (node && node !== document.body) {
              if (node.classList && node.classList.contains('mb-3')) break;
              node = node.parentElement;
            }
            if (!node) return null;
            const label = node.querySelector('label');
            if (!label) return null;
            return (label.textContent || '').trim();
        """
        txt = self.driver.execute_script(script, wrapper)
        if isinstance(txt, str) and txt.strip():
            # normalize multiple spaces/newlines
            return " ".join(txt.split())
        return None

    def _open_widget(self, wrapper: WebElement) -> None:
        inp = wrapper.find_element(By.CSS_SELECTOR, self.fp.input_css)
        # JS click helps with readonly inputs and overlay elements
        inp.click()
        # self.driver.execute_script("arguments[0].click();", inp)

        # Wait for THIS wrapper's calendar to become "open"
        self.wait.until(lambda d: self._is_calendar_open(wrapper))

    def _is_calendar_open(self, wrapper: WebElement) -> bool:
        cal_el = wrapper.find_element(By.CSS_SELECTOR, self.fp.calendar_css)
        cls = cal_el.get_attribute("class") or ""
        return self.fp.open_class in cls.split()

    def _calendar(self, wrapper: WebElement) -> WebElement:
        return wrapper.find_element(By.CSS_SELECTOR, self.fp.calendar_css)

    def _displayed_year_month(self, cal_el: WebElement) -> Tuple[int, int]:
        month_text = cal_el.find_element(By.CSS_SELECTOR, self.fp.month_name_css).text.strip()
        year_val = cal_el.find_element(By.CSS_SELECTOR, self.fp.year_input_css).get_attribute("value").strip()
        return int(year_val), month_num(month_text)

    def _click_prev(self, cal_el: WebElement) -> None:
        btn = cal_el.find_element(By.CSS_SELECTOR, self.fp.prev_css)
        btn.click()
        # self.driver.execute_script("arguments[0].click();", btn)

    def _click_next(self, cal_el: WebElement) -> None:
        btn = cal_el.find_element(By.CSS_SELECTOR, self.fp.next_css)
        btn.click()

    def _goto_month(self, cal_el: WebElement, target: date, max_steps: int = 240) -> None:
        tgt = (target.year, target.month)
        for _ in range(max_steps):
            cur = self._displayed_year_month(cal_el)
            if cur == tgt:
                return

            if cur < tgt:
                self._click_next(cal_el)
            else:
                self._click_prev(cal_el)

            # let DOM/animation settle
            time.sleep(0.05)

        raise TimeoutError(f"Could not navigate to {tgt} within {max_steps} steps")

    def _click_day(self, cal_el: WebElement, target: date) -> None:
        label = aria_label_for(target)
        day_css = f'{self.fp.day_css}[aria-label="{label}"]'
        day = cal_el.find_element(By.CSS_SELECTOR, day_css)

        # Optional safety: avoid disabled
        cls = day.get_attribute("class") or ""
        if "flatpickr-disabled" in cls:
            raise ValueError(f"Date is disabled: {label}")

        day.click()