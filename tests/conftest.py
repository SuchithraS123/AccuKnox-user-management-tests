import pytest
from pages.admin_page import AdminPage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def login_page(page):
    return LoginPage(page)


@pytest.fixture(scope="function")
def admin_page(page):
    return AdminPage(page)
