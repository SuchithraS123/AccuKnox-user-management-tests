from playwright.sync_api import Page


class LoginPage:
    BASE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    def __init__(self, page: Page):
        self.page = page

    def goto(self) -> None:
        self.page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
        self.page.get_by_placeholder("Username").first.wait_for(state="visible", timeout=15000)
        self.page.get_by_placeholder("Password").first.wait_for(state="visible", timeout=15000)

    def _get_field(self, label: str):
        locator = self.page.get_by_placeholder(label)
        if locator.count() > 0:
            return locator.first
        return self.page.get_by_label(label).first

    def login(self, username: str, password: str) -> None:
        self._get_field("Username").fill(username)
        self._get_field("Password").fill(password)
        self.page.get_by_role("button", name="Login").first.click()
        self.page.get_by_text("Dashboard").first.wait_for(state="visible", timeout=15000)

    def is_logged_in(self) -> bool:
        return self.page.get_by_text("Dashboard").count() > 0
