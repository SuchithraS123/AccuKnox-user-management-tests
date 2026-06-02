import time

import pytest
from pages.admin_page import AdminPage
from pages.login_page import LoginPage
from pages.pim_page import PIMPage
from shared_data import shared_data


@pytest.fixture(scope="function")
def login_page(page):
    return LoginPage(page)


@pytest.fixture(scope="function")
def admin_page(page):
    return AdminPage(page)


@pytest.fixture(scope="function")
def pim_page(page):
    return PIMPage(page)


@pytest.fixture(scope="function")
def dynamic_user(login_page, admin_page, pim_page):
    username = shared_data.get("username")
    login_page.goto()
    login_page.login("Admin", "admin123")

    if username:
        admin_page.go_to_admin()
        return username

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
    shared_data["username"] = username
    shared_data["employee_name"] = employee_name

    admin_page.create_user(
        role="ESS",
        employee_name=employee_name,
        status="Enabled",
        username=username,
        password="Test@1234",
    )

    return username
