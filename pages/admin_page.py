from playwright.sync_api import Page


class AdminPage:
    def __init__(self, page: Page):
        self.page = page

    def go_to_admin(self) -> None:
        if self.page.get_by_role("link", name="Admin").count() > 0:
            self.page.get_by_role("link", name="Admin").first.click()
        else:
            self.page.get_by_text("Admin").first.click()
        self.page.wait_for_selector("text=System Users")

    def click_add(self) -> None:
        self.page.get_by_role("button", name="Add").click()
        self.page.wait_for_selector("text=Add User")

    def _select_dropdown(self, label: str, option: str) -> None:
        locator = self.page.get_by_label(label)
        if locator.count() > 0:
            locator.click()
        else:
            self.page.get_by_text(label).first.click()
        self.page.get_by_role("option", name=option).click()

    def add_user(self, role: str, employee_name: str, status: str, username: str, password: str) -> None:
        self.click_add()
        self._select_dropdown("User Role", role)
        self._get_input("Employee Name").fill(employee_name)
        self._select_dropdown("Status", status)
        self._get_input("Username").fill(username)
        self._get_input("Password").fill(password)
        self._get_input("Confirm Password").fill(password)
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_selector("text=Successfully")

    def _get_input(self, label: str):
        locator = self.page.get_by_placeholder(label)
        if locator.count() > 0:
            return locator
        return self.page.get_by_label(label)

    def search_user(self, username: str) -> None:
        self._get_input("Username").fill(username)
        self.page.get_by_role("button", name="Search").click()
        self.page.wait_for_load_state("networkidle")

    def is_user_present(self, username: str) -> bool:
        return self.page.get_by_text(username).count() > 0

    def is_no_records_found(self) -> bool:
        return self.page.get_by_text("No Records Found").count() > 0

    def edit_user(self, username: str) -> None:
        self.search_user(username)
        row = self.page.get_by_text(username).first.locator("xpath=ancestor::div[contains(@class,'oxd-table-row')]")
        row.get_by_role("button", name="Edit").click()
        self.page.wait_for_selector("text=Edit User")

    def update_user_role(self, role: str) -> None:
        self._select_dropdown("User Role", role)
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_selector("text=Successfully")

    def update_user_status(self, status: str) -> None:
        self._select_dropdown("Status", status)
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_selector("text=Successfully")

    def update_username(self, new_username: str, password: str) -> None:
        self._get_input("Username").fill(new_username)
        self._get_input("Password").fill(password)
        self._get_input("Confirm Password").fill(password)
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_selector("text=Successfully")

    def delete_user(self, username: str) -> None:
        self.search_user(username)
        row = self.page.get_by_text(username).first.locator("xpath=ancestor::div[contains(@class,'oxd-table-row')]")
        row.locator('input[type="checkbox"]').check()
        self.page.get_by_role("button", name="Delete").click()
        self.page.get_by_role("button", name="Yes, Delete").click()
        self.page.wait_for_selector("text=Successfully")
