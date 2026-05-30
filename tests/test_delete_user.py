from pages.login_page import LoginPage
from pages.admin_page import AdminPage


def test_tc_12_delete_user(page):
    login_page = LoginPage(page)
    admin_page = AdminPage(page)

    login_page.goto()
    login_page.login("Admin", "admin123")
    admin_page.go_to_admin()
    admin_page.delete_user("testuser02")
    admin_page.search_user("testuser02")

    assert not admin_page.is_user_present("testuser02"), "User should be deleted and not appear in search results"
