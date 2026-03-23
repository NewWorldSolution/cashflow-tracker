MESSAGES = {
    # Navigation
    "nav_brand": "cashflow-tracker",
    "nav_transactions": "Transactions",
    "nav_new": "+ New",
    "nav_sign_out": "Sign out",
    "sandbox_banner": "SANDBOX — this is a test environment. Data may be discarded.",

    # Dashboard
    "dashboard_title": "Dashboard",
    "dashboard_opening_balance": "Opening Balance",
    "dashboard_as_of": "as of",
    "dashboard_not_set": "Not set",
    "dashboard_total_income": "Total Income",
    "dashboard_total_expenses": "Total Expenses",
    "dashboard_transactions": "Transactions",
    "dashboard_active": "active",
    "dashboard_voided": "canceled",
    "dashboard_new_transaction": "+ New Transaction",
    "dashboard_view_all": "View All Transactions",
    "dashboard_recent": "Recent Transactions",
    "dashboard_no_transactions": "No transactions yet.",

    # Transaction form
    "form_title": "New transaction",
    "form_date": "Date",
    "form_direction": "Transaction Type",
    "form_income": "Income",
    "form_expense": "Expense",
    "form_amount": "Amount",
    "form_amount_helper": "Enter gross amount (VAT included)",
    "form_category": "Category",
    "form_category_placeholder": "— select —",
    "form_payment_method": "Payment Method",
    "form_income_type": "Income Type",
    "form_income_type_internal": "Internal",
    "form_income_type_external": "External",
    "form_vat_rate": "VAT Rate (%)",
    "form_vat_deductible": "VAT Deductible (%)",
    "form_description": "Description",
    "form_description_required": "(required)",
    "form_description_placeholder": "Optional notes...",
    "form_save": "Save Transaction",
    "form_cancel": "Cancel",
    "form_card_reminder": (
        "Log gross amount. Card commission is logged separately"
        " at month end from terminal invoice."
    ),
    "form_error_heading": "Please fix the following errors:",

    # Correction form
    "correction_reason_label": "Reason for correction (required)",
    "correction_reason_placeholder": "What is being corrected and why?",

    # Transaction list
    "list_title": "Transactions",
    "list_new": "+ New Transaction",
    "list_show_active_only": "Show Active Only",
    "list_show_all": "Show All (incl. canceled)",
    "list_split_view": "Split View",
    "list_combined_view": "Combined View",
    "list_col_id": "#",
    "list_col_date": "Date",
    "list_col_category": "Category",
    "list_col_direction": "Type",
    "list_col_amount": "Amount",
    "list_col_payment": "Payment",
    "list_col_for_accountant": "For accountant",
    "list_col_logged_by": "Logged by",
    "list_col_status": "Status",
    "list_no_transactions": "No transactions yet.",
    "list_create_first": "Create your first transaction",
    "list_income": "Income",
    "list_expenses": "Expenses",
    "list_no_income": "No income transactions",
    "list_no_expenses": "No expense transactions",

    # Badges
    "badge_active": "Active",
    "badge_voided": "Canceled",
    "badge_corrected": "Corrected",

    # Transaction detail
    "detail_title": "Transaction",
    "detail_back": "← Back to list",
    "detail_date": "Date",
    "detail_direction": "Transaction type",
    "detail_category": "Category",
    "detail_amount_gross": "Amount (gross)",
    "detail_vat_rate": "VAT rate",
    "detail_income_type": "Income type",
    "detail_vat_deductible": "VAT deductible",
    "detail_payment": "Payment",
    "detail_description": "Description",
    "detail_logged_by": "Logged by",
    "detail_created_at": "Created at",
    "detail_correct": "Correct",
    "detail_void": "Cancel",
    "detail_correction_of": "This transaction is a correction of",

    # Accountant
    "for_accountant_label": "For accountant",
    "for_accountant_yes": "Yes",
    "for_accountant_no": "No",

    # Cancellation details (shown when transaction is canceled without correction)
    "void_details_title": "Cancellation Details",
    "void_reason": "Cancellation reason",
    "voided_by": "Canceled by",
    "voided_at": "Canceled at",
    "replaced_by": "Replaced by",

    # Correction details (shown when transaction was corrected)
    "correction_details_title": "Correction Details",
    "correction_reason": "Correction reason",
    "corrected_by": "Corrected by",
    "corrected_at": "Corrected at",

    # Cancel page
    "void_title": "Cancel Transaction",
    "void_warning": (
        "This action cannot be undone."
        " The transaction will be marked as canceled."
    ),
    "void_reason_label": "Reason for canceling (required)",
    "void_reason_placeholder": "Why is this transaction being canceled?",
    "void_submit": "Cancel Transaction",
    "void_cancel": "Cancel",

    # Auth
    "login_title": "Sign in",
    "login_username": "Username",
    "login_password": "Password",
    "login_submit": "Sign in",

    # Settings
    "settings_title": "Opening Balance Setup",
    "settings_description": "Set the starting cash position before logging transactions.",
    "settings_balance_label": "Opening balance (PLN)",
    "settings_date_label": "As of date",
    "settings_save": "Save opening balance",

    # Flash messages
    "flash_transaction_saved": "Transaction saved successfully.",
    "flash_transaction_voided": "Transaction canceled.",
    "flash_transaction_corrected": (
        "Transaction corrected. Original has been canceled."
    ),

    # Language
    "lang_switch_pl": "PL",
    "lang_switch_en": "EN",

    # Enum display labels
    "direction_income": "Income",
    "direction_expense": "Expense",
    "payment_cash": "Cash",
    "payment_card": "Card",
    "payment_transfer": "Transfer",
    "income_type_external": "External",
    "income_type_internal": "Internal",

    # Category labels
    "category_services": "Services",
    "category_products": "Products sold",
    "category_internal_transfer": "Internal transfer",
    "category_other_income": "Other income",
    "category_marketing": "Marketing & advertising",
    "category_marketing_commission": "Sales commissions",
    "category_rent": "Rent & premises",
    "category_utilities": "Utilities",
    "category_renovation": "Renovation & repairs",
    "category_office_supplies": "Office supplies",
    "category_cleaning": "Cleaning services",
    "category_consumables": "Operational consumables",
    "category_equipment": "Equipment & tools",
    "category_contractor_fees": "Contractor & educator fees",
    "category_taxes": "Taxes & ZUS",
    "category_it_software": "IT & software",
    "category_salaries": "Salaries & employee costs",
    "category_transport_vehicle": "Vehicle & petrol",
    "category_transport_travel": "Travel & transport",
    "category_training": "Training & education",
    "category_inventory": "Inventory purchases",
    "category_other_expense": "Other expense",
}

VALIDATION_ERRORS = {
    "Date is required.": "Date is required.",
    "Date must be a valid YYYY-MM-DD value.": "Date must be a valid YYYY-MM-DD value.",
    "Direction must be income or expense.": "Direction must be income or expense.",
    "Amount must be a positive number.": "Amount must be a positive number.",
    "Amount must be greater than 0.": "Amount must be greater than 0.",
    "Category must be a valid category id.": "Category must be a valid category id.",
    "Payment method must be cash, card, or transfer.": (
        "Payment method must be cash, card, or transfer."
    ),
    "VAT rate must be one of 0, 5, 8, or 23.": (
        "VAT rate must be one of 0, 5, 8, or 23."
    ),
    "Income type is required for income transactions.": (
        "Income type is required for income transactions."
    ),
    "Income type must be internal or external.": (
        "Income type must be internal or external."
    ),
    "VAT deductible percentage must be empty for income transactions.": (
        "VAT deductible percentage must be empty for income transactions."
    ),
    "Income type must be empty for expense transactions.": (
        "Income type must be empty for expense transactions."
    ),
    "VAT deductible percentage is required for expense transactions.": (
        "VAT deductible percentage is required for expense transactions."
    ),
    "VAT deductible percentage must be one of 0, 50, or 100.": (
        "VAT deductible percentage must be one of 0, 50, or 100."
    ),
    "Internal income must use a VAT rate of 0.": (
        "Internal income must use a VAT rate of 0."
    ),
    "Internal income must use cash as payment method.": (
        "Internal income must use cash as payment method."
    ),
    "Category direction must match transaction direction.": (
        "Category direction must match transaction direction."
    ),
    "This category is not available for manual transactions.": (
        "This category is not available for manual transactions."
    ),
    "Description is required for other_expense and other_income.": (
        "Description is required for other_expense and other_income."
    ),
    "logged_by must be a valid user id.": "logged_by must be a valid user id.",
    "Correction reason is required.": "Correction reason is required.",
    # Auth errors
    "Username and password are required": "Username and password are required",
    "Invalid credentials": "Invalid credentials",
    # Settings errors
    "Opening balance must be greater than zero.": (
        "Opening balance must be greater than zero."
    ),
    "Date must be in YYYY-MM-DD format (e.g. 2026-01-01).": (
        "Date must be in YYYY-MM-DD format (e.g. 2026-01-01)."
    ),
    # Void errors
    "Transaction not found.": "Transaction not found.",
    "Transaction is already voided.": "Transaction is already voided.",
    "Void reason is required.": "Void reason is required.",
}
