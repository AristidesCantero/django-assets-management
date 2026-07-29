# AI Test Development Guide

## Objective

Design, implement and maintain professional pytest tests for a Django REST Framework project.

The priority is correctness, maintainability and meaningful business coverage.

---

# General Workflow

For every requested feature or component:

1. Read the related source code.
2. Understand its responsibility.
3. Identify the business rules.
4. Identify dependencies.
5. Choose the appropriate test level.
6. Generate missing tests.
7. Update existing tests if necessary.

Never generate tests without first understanding the code.

---

# Source Code Analysis

Before writing tests inspect:

- models.py
- serializers.py
- views.py
- services.py
- permissions.py
- validators.py
- managers.py
- urls.py

If additional modules are imported, inspect those as well.

Follow the execution flow until the business logic is understood.

---

# Test Level Selection

Choose the simplest test capable of validating the behavior.

Prefer:

1. Unit Test
2. Integration Test
3. End-to-End

Only move to a higher level if required.

---

# Unit Tests

Use for isolated business logic.

Typical targets:

- Services
- Validators
- Managers
- Permissions
- Model methods
- Utility functions

Avoid database access whenever possible.

Mock external services only.

---

# Integration Tests

Use when multiple backend components collaborate.

Typical targets:

- APIViews
- Serializers
- Authentication
- ORM
- Transactions

Verify:

- HTTP responses
- Database changes
- Permissions
- Validation

---

# End-to-End Tests

Create only for critical user workflows.

Examples:

- Registration
- Login
- Password reset
- Business creation
- Invitation acceptance

Avoid creating E2E tests for simple CRUD operations.

---

# Test Discovery

For every class or function identify:

- Success scenarios
- Validation failures
- Permission failures
- Boundary cases
- Error handling

Generate one or more tests for each scenario.

---

# Assertions

Assert only observable behavior.

Prefer:

- Returned values
- Raised exceptions
- HTTP status codes
- Response body
- Database state

Avoid testing implementation details.

---

# Existing Tests

Before creating a new test:

- Search for existing tests.
- Extend them if appropriate.
- Avoid duplicated coverage.

Do not create redundant tests.

---

# Project Structure

Use the following structure:

tests/

    conftest.py

    factories.py

    test_models.py

    test_services.py

    test_serializers.py

    test_permissions.py

    test_views.py

    test_validators.py

Create missing files if they do not exist.

---

# Fixtures

Reuse fixtures whenever possible.

Create shared fixtures inside:

tests/conftest.py

Typical fixtures:

- users
- businesses
- authenticated clients
- permissions
- roles
- common objects

Avoid duplicated setup.

---

# Factories

If object creation becomes repetitive:

Create or update:

tests/factories.py

Move reusable object creation into factories.

---

# Naming

Use descriptive names.

Example:

test_admin_can_invite_member

test_worker_cannot_delete_business

test_duplicate_email_returns_validation_error

Avoid generic names.

---

# Output

For every generated test include:

- Why it exists.
- What business rule it validates.
- Why the chosen test level is appropriate.

Then generate the pytest implementation.

---

# If Information Is Missing

If the source code does not clearly define the expected behavior:

Do not invent business rules.

Instead:

- Explain what information is missing.
- Infer only obvious framework behavior.
- Ask for clarification when necessary.

---

# Code Quality

Generated tests must be:

- Small
- Independent
- Deterministic
- Readable
- Easy to maintain

Prefer many focused tests instead of large tests.

Always follow pytest best practices.
