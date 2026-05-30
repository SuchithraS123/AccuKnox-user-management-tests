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

## Playwright version used

- `playwright==1.60.0`
- `pytest==9.0.3`
- `pytest-playwright==0.8.0`

## Notes

- The tests currently target the OrangeHRM demo site at `https://opensource-demo.orangehrmlive.com/`.
- If selectors need adjustment for your target application, update the locators in `pages/login_page.py` and `pages/admin_page.py`.
- Test data values are based on the provided TC list, including `Admin/admin123`, `testuser01`, and `testuser02`.
