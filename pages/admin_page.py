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

    def _find_form_group(self, label: str):
        label_locator = self.page.locator(f"label:has-text('{label}')").first
        return label_locator.locator("xpath=ancestor::div[contains(@class,'oxd-input-group')]" ).first

    def _select_dropdown(self, label: str, option: str) -> None:
        group = self._find_form_group(label)
        dropdown = group.locator(".oxd-select-text").first
        dropdown.click()
        self.page.get_by_role("option", name=option).click()

    def _fill_autocomplete(self, label: str, value: str) -> None:
        input_field = self._get_input(label)
        input_field.click()
        input_field.fill("")
        input_field.type(value, delay=50)
        self.page.wait_for_function(
            '''() => {
                const opts = document.querySelectorAll('div.oxd-autocomplete-dropdown div.oxd-autocomplete-option');
                return Array.from(opts).some(opt => opt.textContent && !opt.textContent.includes('Searching'));
            }''',
            timeout=10000,
        )
        option = self.page.locator('div.oxd-autocomplete-dropdown div.oxd-autocomplete-option', has_text=value).first
        if option.count() == 0:
            option = self.page.locator('div.oxd-autocomplete-dropdown div.oxd-autocomplete-option').first
        option.click()

    def add_user(self, role: str, employee_name: str, status: str, username: str, password: str) -> None:
        self.click_add()
        self._select_dropdown("User Role", role)
        self._fill_autocomplete("Employee Name", employee_name)
        self._select_dropdown("Status", status)
        self._get_input("Username").fill(username)
        self._get_input("Password").fill(password)
        self._get_input("Confirm Password").fill(password)
        self.page.get_by_role("button", name="Save").click()
        # Wait for success message - try multiple selectors
        try:
            self.page.wait_for_selector("text=Successfully Saved", timeout=5000)
        except:
            # If exact text not found, wait for any success message
            self.page.wait_for_selector("text=Success", timeout=5000)

    def _get_input(self, label: str):
        group = self._find_form_group(label)
        if group.count() > 0 and group.locator("input").count() > 0:
            return group.locator("input").first
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
        # Find and click the edit icon (pencil icon) in the Actions column - typically second button
        # The first button is usually delete, second is edit
        actions_cell = row.locator(".oxd-table-cell-actions")
        buttons = actions_cell.locator("button")
        if buttons.count() > 1:
            # Click the second button (edit/pencil icon)
            buttons.nth(1).click()
        else:
            # Fallback to first button if only one exists
            buttons.first.click()
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
