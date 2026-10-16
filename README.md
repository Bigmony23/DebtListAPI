DebtListAPI
A Python API for managing personal debts.

[![Python Package](https://img.shields.io/pypi/v/debtlistapi.svg)](https://pypi.org/project/debtlistapi/)
[![Build Status](https://travis-ci.org/Bigmony23/DebtListAPI.svg?branch=master)](https://travis-ci.org/Bigmony23/DebtListAPI)

DebtListAPI is a Python-based RESTful API designed to help individuals track and manage their personal debts. It provides endpoints for creating, retrieving, updating, and deleting debt records. This API is suitable for developers building personal finance applications or individuals who want a structured way to monitor their financial obligations.

*   **CRUD Operations:** Full Create, Read, Update, and Delete functionality for debt entries.
*   **Debt Categorization:** Assign categories to debts for better organization.
*   **Due Date Tracking:** Monitor upcoming payment deadlines.
*   **Status Updates:** Mark debts as paid, partially paid, or outstanding.
*   **User-Friendly API:** Simple and intuitive endpoints for easy integration.

```bash
pip install debtlistapi
```

```python
from debtlistapi import DebtListAPI

api = DebtListAPI()

# Add a new debt
api.add_debt(
    name="Credit Card Payment",
    amount=1200.50,
    due_date="2023-12-15",
    category="Credit Card"
)

# Get all debts
all_debts = api.get_all_debts()
print(all_debts)

# Get a specific debt by ID
debt_id = 1 # Assuming the first debt added has ID 1
specific_debt = api.get_debt(debt_id)
print(specific_debt)
```

Refer to the `CONTRIBUTING.md` file for details on how to contribute to this project.

MIT License
