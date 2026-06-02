from pages.admin_page import AdminPage


def test_tc_12_delete_user(page, admin_page, dynamic_user):
    username = dynamic_user

    admin_page.delete_user(username)
    admin_page.search_user(username)

    assert not admin_page.is_user_present(username), "User should be deleted and not appear in search results"
