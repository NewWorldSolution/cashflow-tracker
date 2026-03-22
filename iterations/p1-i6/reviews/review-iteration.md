# QA Review — P1-I6: Polish i18n + voided_at
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-6`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i6/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 6. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. i18n foundation: `translate()`, `translate_error()`, `get_messages()` in `app/i18n/__init__.py`
2. English dictionary: `MESSAGES` + `VALIDATION_ERRORS` in `app/i18n/en.py`
3. Template extraction: all hardcoded strings replaced with `{{ t('key') }}`
4. Polish translation: complete `pl.py` with `MESSAGES` + `VALIDATION_ERRORS`
5. Language switcher: PL | EN toggle in nav, `/lang/{locale}` route
6. Locale-aware formatting: `format_date()` and `format_amount()` per locale
7. `voided_at TIMESTAMP` column with migration, service/route changes, 3 new tests
8. Validation errors translated at route layer (validation.py unchanged)
9. Flash messages translated at render time
10. No business logic changes, no calculation changes

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-6
git pull origin feature/phase-1/iteration-6
```

### Step 2 — Full suite and lint

```bash
pytest -v
# Expected: 101 passed, 0 failed (98 existing + 3 new voided_at tests)

ruff check .
# Expected: clean
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected implementation files (all must be present):

```text
app/i18n/__init__.py
app/i18n/en.py
app/i18n/pl.py
app/main.py
app/templates/base.html
app/templates/dashboard.html
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/templates/auth/login.html
app/templates/settings/opening_balance.html
app/routes/transactions.py
app/routes/auth.py
app/routes/settings.py
app/services/transaction_service.py
db/schema.sql
db/init_db.py
static/style.css
tests/test_transactions.py
```

Iteration planning/docs files will also appear in the diff — this is expected:

```text
iterations/p1-i6/prompt.md
iterations/p1-i6/tasks.md
iterations/p1-i6/run.md
iterations/p1-i6/prompts/*.md
iterations/p1-i6/reviews/*.md
```

**Must NOT be modified (frozen files):**

```text
app/services/validation.py
app/services/calculations.py
app/services/auth_service.py
seed/categories.sql
seed/users.sql
static/form.js
tests/test_auth.py
tests/test_init_db.py
tests/test_validation.py
tests/test_calculations.py
```

Any frozen file appearing in the diff = `BLOCKED`.

### Step 4 — Architecture checks

```bash
# No business logic in templates
grep -rn "db\.\|execute\|sqlite3\|validate_\|void_transaction" app/templates/
# Expected: no output

# No stored derived values
grep -n "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" app/routes/transactions.py
# Pre-existing in GET list handler — verify not in any new INSERT/UPDATE

# validation.py must be unchanged
git diff main -- app/services/validation.py
# Expected: no output

# No hard deletes
grep -rn "DELETE FROM" app/
# Expected: no output
```

### Step 5 — i18n completeness checks

```bash
# Count keys in en.py MESSAGES
grep -c "\".*\":" app/i18n/en.py
# Count keys in pl.py MESSAGES
grep -c "\".*\":" app/i18n/pl.py
# Counts should be very close (same keys in both)
```

Verify by code inspection:

- [ ] Every hardcoded string in templates replaced with `{{ t('key') }}`
- [ ] Free-text content (descriptions, void reasons, usernames) NOT wrapped in `t()`
- [ ] Category labels from database NOT wrapped in `t()`
- [ ] Form input values NOT formatted (date picker needs ISO, amount needs decimal)
- [ ] `data-*` attributes NOT formatted

### Step 6 — Translation quality checks

Verify by reading `pl.py`:

- [ ] All translations are professional Polish (business context)
- [ ] No English text left untranslated in `pl.MESSAGES`
- [ ] `VALIDATION_ERRORS` has Polish translations for all validation.py strings
- [ ] Polish date format: `dd.mm.yyyy`
- [ ] Polish amount format: `1 234,56` (non-breaking space + comma decimal)

### Step 7 — voided_at checks

Verify by code inspection:

- [ ] `voided_at TIMESTAMP` column in `db/schema.sql` after `voided_by`
- [ ] Migration in `db/init_db.py` is idempotent (try/except)
- [ ] `void_transaction()` sets `voided_at = CURRENT_TIMESTAMP`
- [ ] Correct flow sets `voided_at` on original transaction
- [ ] `detail.html` displays `voided_at` with `{% if t.voided_at %}` guard
- [ ] 3 new tests: void sets timestamp, correct sets timestamp, active has NULL

### Step 8 — Functional checks

- [ ] Language switcher (PL | EN) visible in nav
- [ ] `/lang/en` and `/lang/pl` in EXEMPT_PATHS
- [ ] Language preference persists in session
- [ ] Default locale is `"pl"`
- [ ] Switching to English shows all text in English
- [ ] Switching to Polish shows all text in Polish
- [ ] Flash messages translate correctly
- [ ] Validation errors translate correctly
- [ ] Inline JS strings in list.html use template-rendered variables

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

Full list with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Architecture Violations

If none: `None.`

### 5. Acceptance Criteria Check

- [PASS|FAIL] pytest: 101 passed, 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] i18n foundation: translate(), translate_error(), get_messages()
- [PASS|FAIL] English dictionary complete (MESSAGES + VALIDATION_ERRORS)
- [PASS|FAIL] all templates extracted (no hardcoded English strings)
- [PASS|FAIL] Polish translation complete (every en.py key has pl.py equivalent)
- [PASS|FAIL] language switcher works (PL | EN)
- [PASS|FAIL] locale-aware date formatting (Polish dd.mm.yyyy, English ISO)
- [PASS|FAIL] locale-aware amount formatting (Polish space+comma, English comma+period)
- [PASS|FAIL] form inputs remain unformatted
- [PASS|FAIL] validation errors translated at route layer
- [PASS|FAIL] flash messages translated at render time
- [PASS|FAIL] validation.py unchanged (frozen)
- [PASS|FAIL] voided_at column in schema with migration
- [PASS|FAIL] void_transaction() and correct flow set voided_at
- [PASS|FAIL] detail.html displays voided_at
- [PASS|FAIL] 3 new voided_at tests pass
- [PASS|FAIL] no business logic changes
- [PASS|FAIL] frozen files unchanged
- [PASS|FAIL] default locale is Polish

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`
