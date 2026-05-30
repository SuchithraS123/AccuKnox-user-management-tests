from pages.login_page import LoginPage
from pages.admin_page import AdminPage


def test_tc_06_search_newly_created_user_using_username(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.search_user("testuser01")

    assert admin_page.is_user_present("testuser01"), "Newly created user should appear in search results"


def test_tc_07_search_with_non_existing_username(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.search_user("invalid123")

    assert admin_page.is_no_records_found(), "No Records Found should be displayed for an invalid username"
