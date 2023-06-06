import datetime
import os
import sys

from playwright.sync_api import Playwright, sync_playwright, expect


username = os.environ["PARASOL_USERNAME"]
password = os.environ["PARASOL_PASSWORD"]


def run(playwright: Playwright) -> None:
    try:
        start, end = process_date_inputs()
    except Exception:
        raise Exception("Problem parsing input parameters")

    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print("Browser started")
    except Exception:
        raise Exception("Problem initialising playwright browser")

    # Login page
    try:
        page.goto("https://portal.myparasol.co.uk/Login.aspx")
        page.locator("#ctl00_ctl00_mainContent_main_userLogin_UserName").fill(username)
        page.locator("#ctl00_ctl00_mainContent_main_userLogin_Password").fill(password)
        page.get_by_role("button", name="Login now").click()
        print("Login successful")
    except Exception:
        raise Exception("Problem logging in to Parasol")

    # There's often (but not always?) a modal window to close
    try:
        page.get_by_role("button", name="close modal").click()
    except Exception:
        pass

    # Locks page
    try:
        page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
        page.get_by_role("button", name="Create locks").click()
        page.locator(
            "#ctl00_ctl00_mainContent_MainContent_startDate_calendarPicker"
        ).type(start.strftime("%d%m%Y"))
        page.locator("#ctl00_ctl00_mainContent_MainContent_reason").select_option(
            "Waiting for Specific Date"
        )
        page.locator(
            "#ctl00_ctl00_mainContent_MainContent_endDate_calendarPicker"
        ).type(end.strftime("%d%m%Y"))
        page.get_by_role("button", name="Ok").click()
        print(f"Lock created from {start} to {end}")
    except Exception:
        raise Exception("Problem creating lock")

    # Check that the lock was created.
    try:
        page.goto("https://portal.myparasol.co.uk/Portal/Account/Locks.aspx")
        expect(
            page.get_by_text(
                f"Lock for waiting for specific date from {start:%d/%m/%Y} to {end:%d/%m/%Y}",
                exact=True,
            )
        ).to_be_visible()
        print("Lock verified")
    except Exception:
        raise Exception("Problem verifying lock")

    # ---------------------
    context.close()
    browser.close()


def process_date_inputs():
    input_period = os.environ.get("TAX_PERIOD", "Weekly")
    input_start = os.environ.get("TAX_PERIOD_START", "Monday")
    input_end = os.environ.get("TAX_PERIOD_END", "Thursday")

    if input_period.lower() == "monthly":
        start, end = get_monthly_params(input_start, input_end)
    else:
        # Default to weekly
        start, end = get_weekly_params(input_start, input_end)

    # Write calculated values to GHA output
    os.environ["OUTPUT_START_DATE"] = f"{start:%Y-%m-%d}"
    os.environ["OUTPUT_END_DATE"] = f"{end:%Y-%m-%d}"

    return start, end


def get_monthly_params(input_start, input_end):
    today = datetime.date.today()
    a_day_early_next_month = today.replace(day=28) + datetime.timedelta(days=4)

    try:
        start_date = int(input_start)
    except ValueError:
        # Default to the 1st
        start_date = 1
    try:
        end_date = int(input_end)
    except ValueError:
        # Default to the last day of next month
        a_day_early_month_after_next = a_day_early_next_month.replace(day=28) + datetime.timedelta(days=4)
        last_day_next_month = a_day_early_month_after_next - datetime.timedelta(days=a_day_early_month_after_next.day)
        end_date = last_day_next_month.day

    return (
        datetime.date(day=start_date, month=a_day_early_next_month.month, year=a_day_early_next_month.year),
        datetime.date(day=end_date, month=a_day_early_next_month.month, year=a_day_early_next_month.year)
    )


def get_weekly_params(input_start, input_end):
    today = datetime.date.today()

    start_diff = 7 + get_weekday_from_input(input_start)
    start = today + datetime.timedelta(days=start_diff - today.weekday())
    end_diff = get_weekday_from_input(input_end)
    end = start + datetime.timedelta(days=end_diff)

    assert end.weekday() > start.weekday()
    return start, end


def get_weekday_from_input(input):
    """
    Allows inputs like "Monday" | "tuesday" | "wed" | "thu" | "4" | 5
    Returns day of the week integer with Monday == 0
    """
    match input.lower()[:3]:
        case "mon" | "0" | 0:
            weekday = 0
        case "tue" | "1" | 1:
            weekday = 1
        case "wed" | "2" | 2:
            weekday = 2
        case "thu" | "3" | 3:
            weekday = 3
        case "fri" | "4" | 4:
            weekday = 4
        case "sat" | "5" | 5:
            weekday = 5
        case "sun" | "6" | 6:
            weekday = 6
        case _:
            raise Exception("Invalid input")
    return weekday


with sync_playwright() as playwright:
    try:
        run(playwright)
        print("Finished")
        # NB super important these are the last two lines printed
        print(f'{os.environ["OUTPUT_START_DATE"]}')
        print(f'{os.environ["OUTPUT_END_DATE"]}')

    except Exception as e:
        print(e, file=sys.stderr)
        # NB super important these are the last two lines printed
        print(f'{os.environ["OUTPUT_START_DATE"]}')
        print(f'{os.environ["OUTPUT_END_DATE"]}')
        sys.exit(1)
