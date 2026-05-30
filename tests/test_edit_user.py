from pages.login_page import LoginPage
from pages.admin_page import AdminPage


def test_tc_08_edit_user_role(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.edit_user("testuser01")
    admin_page.update_user_role("Admin")

    assert page.get_by_text("Successfully").count() > 0, "Updated role should be saved successfully"


def test_tc_09_edit_user_status(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.edit_user("testuser01")
    admin_page.update_user_status("Disabled")

    assert page.get_by_text("Successfully").count() > 0, "Status update should be saved successfully"


def test_tc_10_edit_username_and_validate_update(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.edit_user("testuser01")
    admin_page.update_username("testuser02", "Test@1234")
    admin_page.search_user("testuser02")

    assert admin_page.is_user_present("testuser02"), "Updated username should appear in search results"


def test_tc_11_verify_updated_user_details(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.edit_user("testuser02")

    assert page.get_by_text("Edit User").count() > 0, "Edit page should open for the updated user"
