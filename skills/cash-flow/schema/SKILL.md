---
# Schema
Status: active
Layer: cash-flow
Purpose: Know the full database schema and the rules that govern it.
---

## Tables

### users
```sql
id                INTEGER PRIMARY KEY AUTOINCREMENT
username          TEXT NOT NULL UNIQUE
password_hash     TEXT NOT NULL
telegram_user_id  TEXT UNIQUE          -- nullable; set up before Phase 5
created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### categories
```sql
category_id                INTEGER PRIMARY KEY
name                       TEXT NOT NULL UNIQUE   -- internal code e.g. petrol
label                      TEXT NOT NULL          -- display name
direction                  TEXT NOT NULL CHECK(direction IN ('income','expense'))
default_vat_rate           REAL NOT NULL
default_vat_deductible_pct REAL                  -- expense categories only
```

### transactions
```sql
id                         INTEGER PRIMARY KEY AUTOINCREMENT
date                       DATE NOT NULL
amount                     DECIMAL(10,2) NOT NULL   -- always gross
direction                  TEXT NOT NULL CHECK(direction IN ('income','expense'))
category_id                INTEGER NOT NULL REFERENCES categories(category_id)
payment_method             TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer'))
vat_rate                   REAL NOT NULL            -- validated in app layer; valid values: 0, 5, 8, 23
income_type                TEXT CHECK(income_type IN ('internal','external'))  -- income rows only
vat_deductible_pct         REAL                     -- expense rows only; enforced NOT NULL in app layer
manual_vat_amount          DECIMAL(10,2)            -- advanced mode only
description                TEXT                     -- mandatory on other_expense / other_income
logged_by                  INTEGER NOT NULL REFERENCES users(id)
is_active                  BOOLEAN NOT NULL DEFAULT TRUE
void_reason                TEXT                     -- mandatory when is_active = FALSE
voided_by                  INTEGER REFERENCES users(id)
replacement_transaction_id INTEGER REFERENCES transactions(id)
created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### settings
```sql
key        TEXT PRIMARY KEY
value      TEXT NOT NULL
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```
Stores: `opening_balance`, `as_of_date`

## Schema rules

### Constraints
- `vat_rate` has no CHECK constraint in the database — validated in application code only
- `vat_deductible_pct` NOT NULL on expense rows enforced in application layer (SQLite sandbox)
- PostgreSQL go-live: add conditional CHECK — `CHECK (direction != 'expense' OR vat_deductible_pct IS NOT NULL)`

### Ordering
- `created_at` is the authoritative ordering field — always use `ORDER BY created_at DESC` for correction and audit queries
- `date` alone is not sufficient for ordering — multiple transactions can share the same date

### Database boundary
| Environment | Database | Data |
|---|---|---|
| Phase 1–4 (sandbox) | SQLite | Non-production — may be discarded |
| Go-live | Azure PostgreSQL | Production from this point |

Schema is identical between both engines. Only the connection string changes. The conditional CHECK constraint is added at go-live only.

## Does NOT
- Define validation rules (see transaction_validator skill)
- Define category data (see docs/concept.md — Category Reference section)
