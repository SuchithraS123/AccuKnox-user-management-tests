import random
from playwright.sync_api import Page


class PIMPage:
    def __init__(self, page: Page):
        self.page = page

    def go_to_pim(self) -> None:
        pim_link = self.page.get_by_role("link", name="PIM")
        if pim_link.count() > 0:
            pim_link.first.wait_for(state="visible", timeout=10000)
            pim_link.first.click()
        else:
            self.page.get_by_text("PIM").first.wait_for(state="visible", timeout=10000)
            self.page.get_by_text("PIM").first.click()
        self.page.get_by_text("Employee Information").first.wait_for(state="visible", timeout=15000)

    def click_add_employee(self) -> None:
        add_button = self.page.get_by_role("button", name="Add").first
        add_button.wait_for(state="visible", timeout=15000)
        add_button.click()
        self.page.get_by_text("Add Employee").first.wait_for(state="visible", timeout=15000)

    def _find_form_group(self, label: str):
        label_locator = self.page.locator(f"label:has-text('{label}')").first
        return label_locator.locator("xpath=ancestor::div[contains(@class,'oxd-input-group')]").first

    def _get_input(self, label: str):
        group = self._find_form_group(label)
        if group.count() > 0 and group.locator("input").count() > 0:
            return group.locator("input").first
        locator = self.page.get_by_placeholder(label)
        if locator.count() > 0:
            return locator.first
        return self.page.get_by_label(label).first

    def create_employee(self, first_name: str, middle_name: str, last_name: str, employee_id: str | None = None) -> str:
        self.click_add_employee()
        self._get_input("First Name").fill(first_name)
        self._get_input("Middle Name").fill(middle_name)
        self._get_input("Last Name").fill(last_name)
        if employee_id is None:
            employee_id = str(random.randint(1000, 9999))
        self._get_input("Employee Id").fill(employee_id)
        self.page.get_by_role("button", name="Save").first.click()
        try:
            self.page.get_by_text("Personal Details").first.wait_for(state="visible", timeout=15000)
        except Exception:
            self.page.wait_for_selector("text=Successfully Saved", timeout=10000)
        full_name = " ".join(name for name in [first_name, middle_name, last_name] if name).strip()
        return full_name
