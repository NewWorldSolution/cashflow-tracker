CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    telegram_user_id TEXT UNIQUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id                INTEGER PRIMARY KEY,
    name                       TEXT NOT NULL UNIQUE,
    label                      TEXT NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('cash_in','cash_out')),
    default_vat_rate           REAL,
    default_vat_deductible_pct REAL,
    parent_id                  INTEGER REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS companies (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,
    slug      TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transactions (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    date                       DATE NOT NULL,
    amount                     DECIMAL(10,2) NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('cash_in','cash_out')),
    category_id                INTEGER NOT NULL REFERENCES categories(category_id),
    company_id                 INTEGER NOT NULL DEFAULT 1 REFERENCES companies(id),
    payment_method             TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer')),
    vat_rate                   REAL,
    cash_in_type               TEXT CHECK(cash_in_type IN ('internal','external')),
    vat_deductible_pct         REAL,
    manual_vat_amount          DECIMAL(10,2),
    vat_mode                   TEXT NOT NULL DEFAULT 'automatic' CHECK(vat_mode IN ('automatic','manual')),
    manual_vat_deductible_amount DECIMAL(10,2),
    customer_type              TEXT NOT NULL CHECK(customer_type IN ('private','company','other')),
    document_flow              TEXT CHECK(document_flow IN ('invoice','receipt','invoice_and_receipt','other_document')),
    description                TEXT,
    for_accountant             BOOLEAN NOT NULL DEFAULT FALSE,
    logged_by                  INTEGER NOT NULL REFERENCES users(id),
    is_active                  BOOLEAN NOT NULL DEFAULT TRUE,
    void_reason                TEXT,
    voided_by                  INTEGER REFERENCES users(id),
    voided_at                  TIMESTAMP,
    replacement_transaction_id INTEGER REFERENCES transactions(id),
    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    key        TEXT NOT NULL,
    old_value  TEXT,
    new_value  TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
