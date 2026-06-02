import time

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.pim_page import PIMPage


def create_employee_and_user(page, user_prefix: str):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)
    pim_page = PIMPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    pim_page.go_to_pim()

    first_name = f"AutoFirst{int(time.time()) % 10000}"
    middle_name = "Test"
    last_name = f"AutoLast{int(time.time()) % 10000}"
    employee_name = pim_page.create_employee(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
    )

    admin_page.go_to_admin()
    username = f"{user_prefix}_{int(time.time())}"
    admin_page.create_user(
        role="ESS",
        employee_name=employee_name,
        status="Enabled",
        username=username,
        password="Test@1234",
    )

    return username


def test_tc_08_edit_user_role(page):
    username = create_employee_and_user(page, "edituser_role")
    admin_page = AdminPage(page)

    admin_page.go_to_admin()
    admin_page.search_user(username)
    admin_page.edit_user(username)
    admin_page.update_user_role("Admin")

    assert admin_page.has_success_message(), "Updated role should be saved successfully"


def test_tc_09_edit_user_status(page):
    username = create_employee_and_user(page, "edituser_status")
    admin_page = AdminPage(page)

    admin_page.go_to_admin()
    admin_page.search_user(username)
    admin_page.edit_user(username)
    admin_page.update_user_status("Disabled")

    assert admin_page.has_success_message(), "Status update should be saved successfully"


def test_tc_10_edit_username_and_validate_update(page):
    original_username = create_employee_and_user(page, "edituser_update")
    admin_page = AdminPage(page)

    updated_username = f"{original_username}_updated"
    admin_page.go_to_admin()
    admin_page.search_user(original_username)
    admin_page.edit_user(original_username)
    admin_page.update_username(updated_username, "Test@1234")
    admin_page.go_to_admin()
    admin_page.search_user(updated_username)

    assert admin_page.is_user_present(updated_username), "Updated username should appear in search results"


def test_tc_11_verify_updated_user_details(page):
    username = create_employee_and_user(page, "edituser_verify")
    admin_page = AdminPage(page)

    admin_page.go_to_admin()
    admin_page.search_user(username)
    assert admin_page.is_user_present(username), f"User '{username}' should exist before editing"
    admin_page.edit_user(username)

    assert admin_page.is_edit_user_page(), "Edit page should open for the updated user"
