# AccuKnox User Management Playwright Tests

## Project Structure

```
AccuKnox-user-management-tests
│
├── pages
│   ├── __init__.py
│   ├── login_page.py
│   └── admin_page.py
│
├── tests
│   ├── conftest.py
│   ├── test_login.py
│   ├── test_add_user.py
│   ├── test_search_user.py
│   ├── test_edit_user.py
│   └── test_delete_user.py
│
├── requirements.txt
├── pytest.ini
└── README.md
```

## Prerequisites

- Python 3.10+ installed
- Windows OS
- Project virtual environment setup

## Setup

1. Open a terminal in the project root:

```powershell
cd d:\projects_github\Testcase_project\AccuKnox-user-management-tests
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Install Playwright browser binaries:

```powershell
.venv\Scripts\python.exe -m playwright install
```

## How to run the test cases

- Run all tests:

```powershell
pytest
```

- Run a specific test file:

```powershell
pytest tests/test_login.py
```

- Run a specific test case by name:

```powershell
pytest -k "tc_01"
```

### Headed mode

The project is configured to open the browser in headed mode by default using `pytest.ini`.

To run tests with a visible browser window manually, use:

```powershell
pytest --headed
```

To run headless instead, remove `--headed` from `pytest.ini` or run:

```powershell
pytest -q
```

## Test Cases Documentation

### Test Case Mapping and Files

The test cases (TC_01 through TC_12) are organized by feature across multiple test files:

| Test File | Test Cases Included | Feature |
|-----------|---------------------|---------|
| `tests/test_login.py` | TC_01 | Login with valid credentials |
| `tests/test_add_user.py` | TC_02, TC_03, TC_04, TC_05 | Navigate to Admin, Add User (valid & negative cases) |
| `tests/test_search_user.py` | TC_06, TC_07 | Search User (valid & negative cases) |
| `tests/test_edit_user.py` | TC_08, TC_09, TC_10, TC_11 | Edit User (role, status, username, verify) |
| `tests/test_delete_user.py` | TC_12 | Delete User |

### Page Objects (Reusable Components)

Flow is maintained through **Page Object Model** pattern:

- **`pages/login_page.py`**
  - `LoginPage` class with `goto()`, `login()`, and `is_logged_in()` methods
  - Handles authentication before any admin operations
  - Waits for dashboard URL (`**/dashboard/index`) to confirm successful login

- **`pages/admin_page.py`**
  - `AdminPage` class with all user management operations
  - Methods: `go_to_admin()`, `click_add()`, `add_user()`, `search_user()`, `edit_user()`, `delete_user()`
  - Includes helper methods: `_find_form_group()`, `_select_dropdown()`, `_fill_autocomplete()`, `_get_input()`
  - Handles complex OrangeHRM form interactions (locator discovery, autocomplete waits, dropdown selections)

### Test Execution Flow

Each test follows this flow:

1. **Initialize**: Create `LoginPage` and `AdminPage` objects using Playwright `page` fixture
2. **Login**: Navigate to login page and authenticate with Admin credentials
3. **Perform Action**: Execute the specific user management operation (add, search, edit, delete)
4. **Wait for State**: Use explicit waits for success messages, form elements, or validation errors
5. **Assert**: Verify the expected outcome

### Wait Strategy

- **Navigation waits**: Wait for dashboard URL after login
- **DOM waits**: Wait for labels, dropdowns, and input fields using `wait_for_selector()`
- **Async waits**: Wait for autocomplete dropdown suggestions using `wait_for_function()`
- **Toast messages**: Wait for success/error toast notifications (e.g., `"Successfully Saved"`)

### Test Data & Configuration

- **`pytest.ini`**: Configures pytest to run from the project root with `pythonpath = .` for package imports
- **`tests/conftest.py`**: Defines pytest fixtures for page objects (`login_page`, `admin_page`)
- **Fixture scope**: Function-level fixtures ensure isolation between tests
- **Dynamic usernames**: Tests use timestamp-based usernames to avoid conflicts on repeated runs

## Playwright version used

- `playwright==1.60.0`
- `pytest==9.0.3`
- `pytest-playwright==0.8.0`

## Notes

- The tests currently target the OrangeHRM demo site at `https://opensource-demo.orangehrmlive.com/`.
- If selectors need adjustment for your target application, update the locators in `pages/login_page.py` and `pages/admin_page.py`.
- Test data values are based on the provided TC list, including `Admin/admin123`, `testuser01`, and `testuser02`.
