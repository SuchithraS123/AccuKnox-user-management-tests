import time

from pages.admin_page import AdminPage
from pages.login_page import LoginPage
from pages.pim_page import PIMPage


def test_tc_02_navigate_to_admin_module(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()

    assert admin_page.is_system_users_page_visible(), "Admin page should open successfully"


def test_tc_03_add_new_user_with_valid_details(page):
    login_page = LoginPage(page)
    pim_page = PIMPage(page)
    admin_page = AdminPage(page)

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
    username = f"testuser01_{int(time.time())}"

    admin_page.create_user(
        role="ESS",
        employee_name=employee_name,
        status="Enabled",
        username=username,
        password="Test@1234",
    )

    assert admin_page.has_success_message(), "User creation should result in a success notification"


def test_tc_04_add_user_with_duplicate_username(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()

    admin_page.add_user(
        role="ESS",
        employee_name="Ganesh Kumar A",
        status="Enabled",
        username="Admin",
        password="Test@1234",
    )

    assert admin_page.has_duplicate_user_error(), "Duplicate username validation should be shown"


def test_tc_05_add_user_with_mandatory_fields_blank(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.click_add()
    admin_page.save_user()

    assert admin_page.has_required_field_error(), "Required field validation should be displayed"
