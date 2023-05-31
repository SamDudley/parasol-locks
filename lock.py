import datetime
import os

from playwright.sync_api import Playwright, sync_playwright, expect


username = os.environ["INPUT_PARASOL-USERNAME"]
password = os.environ["INPUT_PARASOL-PASSWORD"]

today = datetime.date.today()
monday = today + datetime.timedelta(days=7 - today.weekday())
friday = monday + datetime.timedelta(days=4)

assert monday.weekday() == 0
assert friday.weekday() == 4


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    print("Page created")

    # Login page
    page.goto("https://portal.myparasol.co.uk/Login.aspx")
    page.locator("#ctl00_ctl00_mainContent_main_userLogin_UserName").fill(username)
    page.locator("#ctl00_ctl00_mainContent_main_userLogin_Password").fill(password)
    page.get_by_role("button", name="Login now").click()
    page.get_by_role("button", name="close modal").click()
    print("Login successful")

    # Locks page
    page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
    page.get_by_role("button", name="Create locks").click()
    page.locator("#ctl00_ctl00_mainContent_MainContent_startDate_calendarPicker").type(monday.strftime("%d%m%Y"))
    page.locator("#ctl00_ctl00_mainContent_MainContent_reason").select_option("Waiting for Specific Date")
    page.locator("#ctl00_ctl00_mainContent_MainContent_endDate_calendarPicker").type(friday.strftime("%d%m%Y"))
    # page.get_by_role("button", name="Ok").click()
    print(f"Lock created from {monday} to {friday}")

    # Check that the lock was created.
    page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
    expect(page.get_by_text(f"Lock for waiting for specific date from {monday:%d/%m/%Y} to {friday:%d/%m/%Y}", exact=True)).to_be_visible()
    print("Lock checked")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
    print("Finished")
