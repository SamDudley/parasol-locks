import datetime
import os
import sys

from playwright.sync_api import Playwright, sync_playwright, expect


username = os.environ["PARASOL_USERNAME"]
password = os.environ["PARASOL_PASSWORD"]

TAX_PERIOD_WEEKLY = "weekly"
TAX_PERIOD_MONTHLY = "monthly"
period = os.environ.get("TAX_PERIOD", TAX_PERIOD_WEEKLY)
start = os.environ.get("TAX_PERIOD_START")
end = os.environ.get("TAX_PERIOD_END")

today = datetime.date.today()
monday = today + datetime.timedelta(days=7 - today.weekday())
friday = monday + datetime.timedelta(days=4)

assert monday.weekday() == 0
assert friday.weekday() == 4

os.environ["OUTPUT_START_DATE"] = f"{monday:%Y-%m-%d}"
os.environ["OUTPUT_END_DATE"] = f"{friday:%Y-%m-%d}"


def run(playwright: Playwright) -> None:
    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print("Browser started")
    except:
        raise Exception("Problem initialising playwright browser")

    # Login page
    try:
        page.goto("https://portal.myparasol.co.uk/Login.aspx")
        page.locator("#ctl00_ctl00_mainContent_main_userLogin_UserName").fill(username)
        page.locator("#ctl00_ctl00_mainContent_main_userLogin_Password").fill(password)
        page.get_by_role("button", name="Login now").click()
        print("Login successful")
    except:
        raise Exception("Problem logging in to Parasol")

    # There's often (but not always?) a modal window to close
    try:
        page.get_by_role("button", name="close modal").click()
    except:
        pass

    # Locks page
    try:
        page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
        page.get_by_role("button", name="Create locks").click()
        page.locator("#ctl00_ctl00_mainContent_MainContent_startDate_calendarPicker").type(monday.strftime("%d%m%Y"))
        page.locator("#ctl00_ctl00_mainContent_MainContent_reason").select_option("Waiting for Specific Date")
        page.locator("#ctl00_ctl00_mainContent_MainContent_endDate_calendarPicker").type(friday.strftime("%d%m%Y"))
        page.get_by_role("button", name="Ok").click()
        print(f"Lock created from {monday} to {friday}")
    except:
        raise Exception("Problem creating lock")

    # Check that the lock was created.
    try:
        page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
        expect(page.get_by_text(f"Lock for waiting for specific date from {monday:%d/%m/%Y} to {friday:%d/%m/%Y}", exact=True)).to_be_visible()
        print("Lock verified")
    except:
        raise Exception("Problem verifying lock")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    try:
        run(playwright)
        print("Finished")
    except Exception as e:
        print(e)
        sys.exit(1)
