from pages.login_page import LoginPage
from pages.admin_page import AdminPage


def test_tc_02_navigate_to_admin_module(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()

    assert page.get_by_text("System Users").first.is_visible(), "Admin page should open successfully"


def test_tc_03_add_new_user_with_valid_details(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.add_user(
        role="ESS",
        employee_name="Fiona Grace",
        status="Enabled",
        username="testuser01",
        password="Test@1234",
    )

    assert page.get_by_text("Successfully").count() > 0, "Success message should be displayed after creating the user"


def test_tc_04_add_user_with_duplicate_username(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.click_add()
    admin_page._get_input("Username").fill("Admin")
    admin_page._get_input("Password").fill("Test@1234")
    admin_page._get_input("Confirm Password").fill("Test@1234")
    page.get_by_role("button", name="Save").click()

    assert page.get_by_text("Already exists").count() > 0, "Duplicate username validation should be shown"


def test_tc_05_add_user_with_mandatory_fields_blank(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.click_add()
    page.get_by_role("button", name="Save").click()

    assert page.get_by_text("Required").count() > 0, "Required field validation should be displayed"
