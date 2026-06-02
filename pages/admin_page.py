from playwright.sync_api import Page


class AdminPage:
    def __init__(self, page: Page):
        self.page = page

    def go_to_admin(self) -> None:
        admin_link = self.page.get_by_role("link", name="Admin")
        if admin_link.count() > 0:
            admin_link.first.wait_for(state="visible", timeout=10000)
            admin_link.first.click()
        else:
            self.page.get_by_text("Admin").first.wait_for(state="visible", timeout=10000)
            self.page.get_by_text("Admin").first.click()
        self.wait_for_system_users_page()

    def wait_for_system_users_page(self) -> None:
        self.page.get_by_text("System Users").first.wait_for(state="visible", timeout=15000)

    def is_system_users_page_visible(self) -> bool:
        return self.page.get_by_text("System Users").count() > 0

    def click_add(self) -> None:
        add_button = self.page.get_by_role("button", name="Add").first
        add_button.wait_for(state="visible", timeout=15000)
        add_button.click()
        self.page.get_by_text("Add User").first.wait_for(state="visible", timeout=15000)

    def _find_form_group(self, label: str):
        label_locator = self.page.locator(f"label:text-is('{label}')").first
        if label_locator.count() == 0:
            label_locator = self.page.locator(f"label:has-text('{label}')").first
        return label_locator.locator("xpath=ancestor::div[contains(@class,'oxd-input-group')]").first

    def _get_input(self, label: str):
        group = self._find_form_group(label)
        if group.count() > 0 and group.locator("input").count() > 0:
            non_checkbox = group.locator("input:not([type='checkbox'])")
            if non_checkbox.count() > 0:
                return non_checkbox.first
            return group.locator("input").first
        locator = self.page.get_by_placeholder(label)
        if locator.count() > 0:
            return locator.first
        return self.page.get_by_label(label).first

    def _select_dropdown(self, label: str, option: str) -> None:
        group = self._find_form_group(label)
        dropdown = group.locator(".oxd-select-text").first
        dropdown.wait_for(state="visible", timeout=10000)
        dropdown.click()
        option_item = self.page.get_by_role("option", name=option).first
        option_item.wait_for(state="visible", timeout=10000)
        option_item.click()

    def _fill_autocomplete(self, label: str, value: str) -> None:
        input_field = self._get_input(label)
        input_field.wait_for(state="visible", timeout=10000)
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
        option.wait_for(state="visible", timeout=10000)
        option.click()

    def fill_user_details(self, role: str, employee_name: str, status: str, username: str, password: str) -> None:
        self.select_user_role(role)
        self.set_employee_name(employee_name)
        self.select_status(status)
        self.set_username(username)
        self.set_password(password)

    def add_user(self, role: str, employee_name: str, status: str, username: str, password: str) -> None:
        self.click_add()
        self.fill_user_details(role, employee_name, status, username, password)
        self.save_user()

    def create_user(self, role: str, employee_name: str, status: str, username: str, password: str) -> None:
        self.add_user(role, employee_name, status, username, password)

    def select_user_role(self, role: str) -> None:
        self._select_dropdown("User Role", role)

    def set_employee_name(self, employee_name: str) -> None:
        self._fill_autocomplete("Employee Name", employee_name)

    def select_status(self, status: str) -> None:
        self._select_dropdown("Status", status)

    def set_username(self, username: str) -> None:
        self._get_input("Username").fill(username)

    def set_password(self, password: str) -> None:
        self._get_input("Password").fill(password)
        self._get_input("Confirm Password").fill(password)

    def save_user(self) -> None:
        save_button = self.page.get_by_role("button", name="Save").first
        save_button.wait_for(state="visible", timeout=10000)
        save_button.click()
        self.wait_for_success_or_user_list()

    def wait_for_form_loader(self) -> None:
        try:
            self.page.wait_for_selector(".oxd-form-loader", state="hidden", timeout=15000)
        except Exception:
            pass

    def wait_for_success_or_user_list(self) -> None:
        try:
            self.page.wait_for_selector("text=Successfully", timeout=10000)
        except Exception:
            self.wait_for_system_users_page()

    def has_success_message(self) -> bool:
        return self.page.get_by_text("Successfully", exact=False).count() > 0

    def has_validation_message(self, message: str) -> bool:
        return self.page.get_by_text(message, exact=False).count() > 0

    def has_duplicate_user_error(self) -> bool:
        return self.has_validation_message("Already exists")

    def has_required_field_error(self) -> bool:
        return self.has_validation_message("Required")

    def _check_checkbox(self, label: str) -> None:
        group = self._find_form_group(label)
        checkbox = group.locator("input[type='checkbox']").first
        if checkbox.count() > 0:
            if not checkbox.is_checked():
                self.wait_for_form_loader()
                checkbox.check(force=True)
            return
        label_locator = self.page.get_by_label(label)
        if label_locator.count() > 0:
            label_locator.first.click(force=True)

    def search_user(self, username: str) -> None:
        username_input = self._get_input("Username")
        username_input.wait_for(state="visible", timeout=10000)
        username_input.fill(username)
        self.page.get_by_role("button", name="Search").first.click()
        try:
            self.page.wait_for_selector(".oxd-form-loader", state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def is_user_present(self, username: str) -> bool:
        self.page.wait_for_timeout(500)
        try:
            self.page.wait_for_selector(f"text={username}", timeout=10000)
            return self.page.get_by_text(username).count() > 0
        except Exception:
            return False

    def is_no_records_found(self) -> bool:
        self.page.wait_for_selector("text=No Records Found", timeout=10000)
        return self.page.get_by_text("No Records Found").count() > 0

    def edit_user(self, username: str) -> None:
        self.search_user(username)
        row = self.page.locator(f"xpath=//div[contains(@class,'oxd-table-row')][.//div[contains(text(), '{username}')]]").first
        row.wait_for(state="visible", timeout=10000)
        edit_button = row.locator("button[aria-label='Edit'], button[title='Edit'], button:has-text('Edit')")
        if edit_button.count() > 0:
            edit_button.first.click()
        else:
            actions_cell = row.locator(".oxd-table-cell-actions")
            buttons = actions_cell.locator("button")
            if buttons.count() > 1:
                buttons.nth(1).click()
            else:
                buttons.first.click()
        self.page.get_by_text("Edit User").first.wait_for(state="visible", timeout=10000)

    def update_user_role(self, role: str) -> None:
        self._select_dropdown("User Role", role)
        self.page.get_by_role("button", name="Save").click()
        try:
            self.page.wait_for_selector("text=Successfully", timeout=10000)
        except Exception:
            self.page.wait_for_selector("text=System Users", timeout=15000)

    def update_user_status(self, status: str) -> None:
        self._select_dropdown("Status", status)
        self.page.get_by_role("button", name="Save").click()
        try:
            self.page.wait_for_selector("text=Successfully", timeout=10000)
        except Exception:
            self.page.wait_for_selector("text=System Users", timeout=15000)

    def is_edit_user_page(self) -> bool:
        return self.page.get_by_text("Edit User").count() > 0

    def update_username(self, new_username: str, password: str) -> None:
        try:
            self.page.wait_for_selector(".oxd-form-loader", state="hidden", timeout=15000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

        username_input = self._get_input("Username")
        username_input.fill("")
        username_input.fill(new_username)
        self.page.wait_for_timeout(500)
        self._check_checkbox("Change Password ?")
        self.page.wait_for_timeout(300)
        self._get_input("Password").fill(password)
        self._get_input("Confirm Password").fill(password)
        self.page.wait_for_timeout(300)
        self.page.get_by_role("button", name="Save").click()
        try:
            self.page.wait_for_selector(".oxd-form-loader", state="hidden", timeout=15000)
        except Exception:
            pass
        try:
            self.page.wait_for_selector("text=Successfully", timeout=10000)
        except Exception:
            try:
                self.page.wait_for_selector("text=System Users", timeout=10000)
            except Exception:
                pass

    def delete_user(self, username: str) -> None:
        self.search_user(username)
        row = self.page.get_by_text(username).first.locator("xpath=ancestor::div[contains(@class,'oxd-table-row')]")
        row.wait_for(state="visible", timeout=10000)
        checkbox = row.locator('input[type="checkbox"]').first
        if checkbox.count() > 0:
            try:
                checkbox.check(force=True)
            except Exception:
                wrapper = row.locator("span.oxd-checkbox-input").first
                wrapper.click(force=True)
        else:
            wrapper = row.locator("span.oxd-checkbox-input").first
            wrapper.click(force=True)
        self.page.get_by_role("button", name="Delete").click()
        self.page.get_by_role("button", name="Yes, Delete").click()
        try:
            self.page.wait_for_selector("text=Successfully", timeout=10000)
        except Exception:
            self.page.wait_for_selector("text=System Users", timeout=15000)
