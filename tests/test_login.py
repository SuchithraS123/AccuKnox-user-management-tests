from pages.login_page import LoginPage


def test_tc_01_login_with_valid_credentials(page):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login("Admin", "admin123")
    assert login_page.is_logged_in(), "Dashboard should be displayed after login"
