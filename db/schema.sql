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
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    default_vat_rate           REAL NOT NULL,
    default_vat_deductible_pct REAL
);

CREATE TABLE IF NOT EXISTS transactions (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    date                       DATE NOT NULL,
    amount                     DECIMAL(10,2) NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    category_id                INTEGER NOT NULL REFERENCES categories(category_id),
    payment_method             TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer')),
    vat_rate                   REAL NOT NULL,
    income_type                TEXT CHECK(income_type IN ('internal','external')),
    vat_deductible_pct         REAL,
    manual_vat_amount          DECIMAL(10,2),
    description                TEXT,
    logged_by                  INTEGER NOT NULL REFERENCES users(id),
    is_active                  BOOLEAN NOT NULL DEFAULT TRUE,
    void_reason                TEXT,
    voided_by                  INTEGER REFERENCES users(id),
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
