# P1-I8 — Category & Sub-Category Taxonomy

**Status:** Locked 2026-03-24
**Context:** Replaces the 22-category flat list used during testing (P1-I1 through I7). Fresh start — no migration from old categories.

---

## Design Decisions

1. **Two-level hierarchy only** — parent group + subcategory. No deeper nesting.
2. **Only leaf nodes (subcategories) are selectable** in the transaction form.
3. **Parent group is used for analysis/reporting**, subcategory for precision.
4. **UI: two-level picker** — select parent first, then subcategory populates.
5. **Direction renamed:** `income` / `expense` → `cash_in` / `cash_out` throughout (DB, validation, UI, i18n).
6. **`income_type` renamed to `cash_in_type`** — values remain `internal` / `external`, applies only to `cash_in`.
7. **Internal Transfer dropped** — deferred to Phase 2 when per-company balances exist.
8. **Non-Cash / Amortization deferred** — Phase 2 scope.
9. **Catch-all "Other" subcategories are added only where needed** — currently: Other Income, Other Expense, Other Financial Income, Other Financial Costs, Other Services, Other Training Costs.
10. **Fresh start** — old 22 testing categories are discarded entirely.
11. **Slugs are globally unique** — direction-prefixed and parent-prefixed to avoid collisions.
12. **VAT defaults are first-pass pragmatic** — 23% where normal, 0% where obviously non-VAT. May be refined after Phase 1.

---

## Slug Convention

```
Parents:  {direction}_{group}         → ci_services, co_marketing
Children: {direction}_{group}_{item}  → ci_services_test, co_marketing_paid_ads
```

All slugs: lowercase, snake_case, globally unique across both directions.

---

## Cash In

| # | Parent Group | Subcategory | Slug | VAT % | Notes |
|---|-------------|-------------|------|-------|-------|
| 1 | Services | Test | ci_services_test | 23 | |
| 2 | | Package | ci_services_package | 23 | |
| 3 | | Bioresonance | ci_services_bioresonance | 23 | |
| 4 | | Dietetic | ci_services_dietetic | 23 | |
| 5 | | Naturopathic | ci_services_naturopathic | 23 | |
| 6 | Training | Training Income | ci_training_income | 23 | Single child; parent ready for future split |
| 7 | Product Sales | Accessories / Ampulles | ci_products_accessories | 23 | |
| 8 | | Zapper / Chipcard | ci_products_zapper | 23 | |
| 9 | | Supplements | ci_products_supplements | 23 | |
| 10 | | Trikombin | ci_products_trikombin | 23 | |
| 11 | Commissions / Affiliate | Affiliate Income | ci_commissions_affiliate | 23 | |
| 12 | | Partner Commissions | ci_commissions_partner | 23 | |
| 13 | Consulting | Business Consulting | ci_consulting_business | 23 | |
| 14 | | IT Consulting | ci_consulting_it | 23 | |
| 15 | Financial | Loan Repayment Received | ci_financial_loan_repayment_received | 0 | Someone repaying a loan I gave them |
| 16 | | Stock-Exchange Income | ci_financial_stock_exchange | 0 | |
| 17 | | Other Financial Income | ci_financial_other | 0 | |
| 18 | | Loan Taken | ci_financial_loan_taken | 0 | I took a loan from bank/institution |
| 19 | Other Income | Rent | ci_other_rent | 23 | Rental income from property |
| 20 | | Other Income | ci_other_income | 23 | Catch-all, requires description |

**Parent slugs:** `ci_services`, `ci_training`, `ci_products`, `ci_commissions`, `ci_consulting`, `ci_financial`, `ci_other`

**Cash In total: 7 parent groups, 20 subcategories**

**Note:** Cash In has no `vat_deductible_pct` — that field applies only to Cash Out.

---

## Cash Out

| # | Parent Group | Subcategory | Slug | VAT % | Deductible % | Notes |
|---|-------------|-------------|------|-------|-------------|-------|
| 1 | Marketing | Paid Ads | co_marketing_paid_ads | 23 | 100 | |
| 2 | | SEO | co_marketing_seo | 23 | 100 | |
| 3 | | Agent / Referral Fees | co_marketing_agent_fees | 23 | 100 | |
| 4 | Operations | Rent | co_operations_rent | 23 | 100 | Default assumes company invoice; user changes to 0% for private-person rent |
| 5 | | Utilities | co_operations_utilities | 23 | 100 | |
| 6 | | Office Supplies | co_operations_office_supplies | 23 | 100 | |
| 7 | | Transport / Petrol | co_operations_transport | 23 | 50 | Polish mixed-use vehicle rule |
| 8 | | Small Equipment | co_operations_small_equipment | 23 | 100 | |
| 9 | | Maintenance / Repairs | co_operations_maintenance | 23 | 100 | |
| 10 | People Costs | Salaries | co_people_salaries | 0 | 0 | No VAT on payroll |
| 11 | | Bonuses / Additional Payments | co_people_bonuses | 0 | 0 | |
| 12 | | Employee ZUS | co_people_employee_zus | 0 | 0 | |
| 13 | | Employee PIT | co_people_employee_pit | 0 | 0 | |
| 14 | | Contractors | co_people_contractors | 23 | 100 | |
| 15 | Owner / Company Taxes | VAT Payments | co_taxes_vat | 0 | 0 | Pure cash outflow |
| 16 | | Income Tax | co_taxes_income_tax | 0 | 0 | |
| 17 | | Owner ZUS | co_taxes_owner_zus | 0 | 0 | |
| 18 | Services & Subscriptions | Accountant | co_services_accountant | 23 | 100 | |
| 19 | | Software / SaaS | co_services_software | 23 | 100 | |
| 20 | | Other Services | co_services_other | 23 | 100 | |
| 21 | Financial | Bank Fees | co_financial_bank_fees | 0 | 0 | VAT exempt in Poland |
| 22 | | Loan Repayment | co_financial_loan_repayment | 0 | 0 | Repaying a loan I took |
| 23 | | Stock-Exchange Cash Out | co_financial_stock_exchange | 0 | 0 | |
| 24 | | Other Financial Costs | co_financial_other | 0 | 0 | |
| 25 | | Loan Given | co_financial_loan_given | 0 | 0 | I lent money to someone/company |
| 26 | Inventory | Devices for Resale | co_inventory_devices | 23 | 100 | |
| 27 | | Supplements | co_inventory_supplements | 23 | 100 | |
| 28 | | Accessories | co_inventory_accessories | 23 | 100 | |
| 29 | CAPEX | Machines | co_capex_machines | 23 | 100 | |
| 30 | | Equipment | co_capex_equipment | 23 | 100 | |
| 31 | | Renovation / Improvements | co_capex_renovation | 23 | 100 | |
| 32 | Training - Internal | Course Fees | co_training_int_course_fees | 23 | 100 | Learning/development for business team |
| 33 | | Hotel | co_training_int_hotel | 8 | 100 | Polish hotel VAT rate |
| 34 | | Transport | co_training_int_transport | 23 | 100 | |
| 35 | | Food / Catering | co_training_int_food | 8 | 100 | Polish restaurant/catering VAT rate |
| 36 | | Other Training Costs | co_training_int_other | 23 | 100 | |
| 37 | Training - Delivery | Preparation Costs | co_training_del_preparation | 23 | 100 | Costs of delivering training as business activity |
| 38 | | Travel | co_training_del_travel | 23 | 100 | |
| 39 | | Food / Catering | co_training_del_food | 8 | 100 | |
| 40 | | Commissions | co_training_del_commissions | 23 | 100 | |
| 41 | Owner / Private | Private Withdrawals | co_private_withdrawals | 0 | 0 | Owner taking money from company |
| 42 | Other Expense | Other Expense | co_other_expense | 23 | 100 | Catch-all, requires description |

**Parent slugs:** `co_marketing`, `co_operations`, `co_people`, `co_taxes`, `co_services`, `co_financial`, `co_inventory`, `co_capex`, `co_training_int`, `co_training_del`, `co_private`, `co_other`

**Cash Out total: 12 parent groups, 42 subcategories**

---

## Important Rules

- **Inventory vs CAPEX** — always separate. Inventory is goods for resale; CAPEX is long-term assets/improvements.
- **Owner / Private vs `company = private`** — different concepts. `company = private` is for personal life transactions. `Owner / Private > Private Withdrawals` is money leaving the business entity to the owner.
- **Training - Internal vs Training - Delivery** — always separate. Internal = learning costs for team. Delivery = costs of running training as a business service.
- **Other Income and Other Expense** — always require a non-empty description (existing rule, carried forward).
- **Loan tracking** — four subcategories across Cash In and Cash Out form two pairs:
  - Loans I gave: `Cash Out > Financial > Loan Given` ↔ `Cash In > Financial > Loan Repayment Received`
  - Loans I took: `Cash In > Financial > Loan Taken` ↔ `Cash Out > Financial > Loan Repayment`

---

## Grand Total

| Direction | Parent Groups | Subcategories |
|-----------|--------------|---------------|
| Cash In | 7 | 20 |
| Cash Out | 12 | 42 |
| **Total** | **19** | **62** |
