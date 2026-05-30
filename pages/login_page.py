from playwright.sync_api import Page


class LoginPage:
    BASE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    def __init__(self, page: Page):
        self.page = page

    def goto(self) -> None:
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")

    def _get_field(self, label: str):
        locator = self.page.get_by_placeholder(label)
        if locator.count() > 0:
            return locator
        return self.page.get_by_label(label)

    def login(self, username: str, password: str) -> None:
        self._get_field("Username").fill(username)
        self._get_field("Password").fill(password)
        with self.page.expect_navigation(url="**/dashboard/index", timeout=15000):
            self.page.get_by_role("button", name="Login").click()
        self.page.wait_for_url("**/dashboard/index", timeout=15000)

    def is_logged_in(self) -> bool:
        return "/dashboard/index" in self.page.url or self.page.get_by_text("Dashboard").count() > 0
