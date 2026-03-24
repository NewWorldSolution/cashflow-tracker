# P1-I8 Iteration QA Review

Review the merged I8 branch against `main`.

Minimum QA coverage must include:
- category hierarchy migration and picker behavior
- manual VAT mode behavior for expense and income
- internal income restrictions
- correction preserving and allowing changes to category path and VAT mode
- default `for_accountant = on` on create, except internal income
- external income document type:
  - visible only for external income
  - default `receipt`
  - shown in detail view
- pytest green
- ruff clean
