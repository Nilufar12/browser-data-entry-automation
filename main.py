import json
import logging
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_DIR = Path(__file__).parent

ACCOUNTS_FILE = BASE_DIR / "accounts.json"
SITE_FILE = BASE_DIR / "test_site.html"


def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


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

        return True

    except Exception as error:

        logging.error(
            "Account %s failed: %s",
            username,
            error
        )
        return False


def main():

    accounts = load_accounts()

    successful = 0
    failed = 0

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        for account in accounts:

            result = process_account(page, account)

            if result:
                successful += 1
            else:
                failed += 1

        browser.close()

    print()
    print("Automation finished")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()