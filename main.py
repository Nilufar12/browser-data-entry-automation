import csv
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright


logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_DIR = Path(__file__).parent
SITE_FILE = BASE_DIR / "test_site.html"


def load_accounts_from_csv():
    with open(BASE_DIR / "accounts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_report(results):
    report_file = BASE_DIR / "report.csv"

    with open(report_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["username", "status", "error"]
        )

        writer.writeheader()
        writer.writerows(results)


def process_account(page, account):

    username = account["username"]

    logging.info("Starting account: %s", username)

    try:

        page.goto(SITE_FILE.as_uri())

        page.locator("#username").fill(account["username"])
        page.locator("#password").fill(account["password"])

        page.locator("button", has_text="Login").click()

        page.locator("#firstName").fill(account["first_name"])
        page.locator("#lastName").fill(account["last_name"])
        page.locator("#email").fill(account["email"])

        page.locator("button", has_text="Save").click()

        message = page.locator("#message").inner_text()

        if "successfully" not in message:
            raise Exception("Data was not saved")

        logging.info(
            "Account %s processed successfully",
            username
        )

        page.locator("button", has_text="Logout").click()

        return {
            "username": username,
            "status": "success",
            "error": ""
        }

    except Exception as error:

        logging.error(
            "Account %s failed: %s",
            username,
            error
        )

        return {
            "username": username,
            "status": "failed",
            "error": str(error)
        }


def main():

    accounts = load_accounts_from_csv()

    successful = 0
    failed = 0
    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        for account in accounts:

            result = process_account(page, account)

            results.append(result)

            if result["status"] == "success":
                successful += 1
            else:
                failed += 1

        save_report(results)

        browser.close()

    print()
    print("Automation finished")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print("Report saved to report.csv")


if __name__ == "__main__":
    main()