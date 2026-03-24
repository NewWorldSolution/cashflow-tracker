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
    "dashboard_total_cash_in": "Total Cash In",
    "dashboard_total_cash_out": "Total Cash Out",
    "dashboard_transactions": "Transactions",
    "dashboard_active": "active",
    "dashboard_voided": "canceled",
    "dashboard_new_transaction": "+ New Transaction",
    "dashboard_view_all": "View All Transactions",
    "dashboard_recent": "Recent Transactions",
    "dashboard_no_transactions": "No transactions yet.",
    "filter_company": "Company",
    "filter_all_companies": "All companies",

    # Transaction form
    "form_title": "New transaction",
    "form_date": "Date",
    "form_direction": "Transaction Type",
    "form_cash_in": "Cash In",
    "form_cash_out": "Cash Out",
    "form_amount": "Amount",
    "form_amount_helper": "Enter gross amount (VAT included)",
    "form_category": "Category",
    "form_category_group": "Category Group",
    "form_subcategory": "Subcategory",
    "form_category_placeholder": "— select —",
    "select_category_group": "Select category group",
    "select_subcategory": "Select subcategory",
    "form_payment_method": "Payment Method",
    "form_cash_in_type": "Cash-In Type",
    "form_cash_in_type_internal": "Internal",
    "form_cash_in_type_external": "External",
    "form_vat_mode": "VAT Mode",
    "vat_mode_automatic": "Automatic",
    "vat_mode_manual": "Manual",
    "form_vat_rate": "VAT Rate (%)",
    "form_vat_deductible": "VAT Deductible (%)",
    "form_manual_vat_amount": "Manual VAT Amount",
    "form_manual_vat_deductible_amount": "Manual VAT Deductible Amount",
    "form_customer_type": "Customer Type",
    "select_customer_type": "Select customer type",
    "customer_type_private": "Private Person",
    "customer_type_company": "Company",
    "customer_type_other": "Other",
    "form_document_flow": "Document Flow",
    "select_document_flow": "Select document flow",
    "document_flow_invoice": "Invoice",
    "document_flow_receipt": "Receipt",
    "document_flow_invoice_and_receipt": "Invoice and Receipt",
    "document_flow_other_document": "Other Document",
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

    # Company selector
    "form_company": "Company",
    "company_sp": "SP",
    "company_sp_full": "Sole Proprietorship (SP)",
    "company_ltd": "LTD",
    "company_ltd_full": "Limited Company (LTD)",
    "company_ff": "FF",
    "company_ff_full": "Family Foundation (FF)",
    "company_private": "P",
    "company_private_full": "Private (P)",

    # Accountant flag
    "form_for_accountant": "Mark for accountant",

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
    "list_col_company": "Company",
    "list_col_direction": "Type",
    "list_col_amount": "Amount",
    "list_col_payment": "Payment",
    "list_col_for_accountant": "For accountant",
    "list_col_logged_by": "Logged by",
    "list_col_status": "Status",
    "list_no_transactions": "No transactions yet.",
    "list_create_first": "Create your first transaction",
    "list_cash_in": "Cash In",
    "list_cash_out": "Cash Out",
    "list_no_cash_in": "No cash-in transactions",
    "list_no_cash_out": "No cash-out transactions",

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
    "detail_company": "Company",
    "detail_amount_gross": "Amount (gross)",
    "detail_vat_rate": "VAT rate",
    "detail_cash_in_type": "Cash-in type",
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
    "direction_cash_in": "Cash In",
    "direction_cash_out": "Cash Out",
    "payment_cash": "Cash",
    "payment_card": "Card",
    "payment_transfer": "Transfer",
    "cash_in_type_external": "External",
    "cash_in_type_internal": "Internal",

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
    "cat_ci_services": "Services",
    "cat_ci_training": "Training",
    "cat_ci_products": "Product Sales",
    "cat_ci_commissions": "Commissions / Affiliate",
    "cat_ci_consulting": "Consulting",
    "cat_ci_financial": "Financial",
    "cat_ci_other": "Other Income",
    "cat_co_marketing": "Marketing",
    "cat_co_operations": "Operations",
    "cat_co_people": "People Costs",
    "cat_co_taxes": "Owner / Company Taxes",
    "cat_co_services": "Services & Subscriptions",
    "cat_co_financial": "Financial",
    "cat_co_inventory": "Inventory",
    "cat_co_capex": "CAPEX",
    "cat_co_training_int": "Training - Internal",
    "cat_co_training_del": "Training - Delivery",
    "cat_co_private": "Owner / Private",
    "cat_co_other": "Other Expense",
    "cat_ci_services_test": "Test",
    "cat_ci_services_package": "Package",
    "cat_ci_services_bioresonance": "Bioresonance",
    "cat_ci_services_dietetic": "Dietetic",
    "cat_ci_services_naturopathic": "Naturopathic",
    "cat_ci_training_income": "Training Income",
    "cat_ci_products_accessories": "Accessories / Ampulles",
    "cat_ci_products_zapper": "Zapper / Chipcard",
    "cat_ci_products_supplements": "Supplements",
    "cat_ci_products_trikombin": "Trikombin",
    "cat_ci_commissions_affiliate": "Affiliate Income",
    "cat_ci_commissions_partner": "Partner Commissions",
    "cat_ci_consulting_business": "Business Consulting",
    "cat_ci_consulting_it": "IT Consulting",
    "cat_ci_financial_loan_repayment_received": "Loan Repayment Received",
    "cat_ci_financial_stock_exchange": "Stock-Exchange Income",
    "cat_ci_financial_other": "Other Financial Income",
    "cat_ci_financial_loan_taken": "Loan Taken",
    "cat_ci_other_rent": "Rent",
    "cat_ci_other_income": "Other Income",
    "cat_co_marketing_paid_ads": "Paid Ads",
    "cat_co_marketing_seo": "SEO",
    "cat_co_marketing_agent_fees": "Agent / Referral Fees",
    "cat_co_operations_rent": "Rent",
    "cat_co_operations_utilities": "Utilities",
    "cat_co_operations_office_supplies": "Office Supplies",
    "cat_co_operations_transport": "Transport / Petrol",
    "cat_co_operations_small_equipment": "Small Equipment",
    "cat_co_operations_maintenance": "Maintenance / Repairs",
    "cat_co_people_salaries": "Salaries",
    "cat_co_people_bonuses": "Bonuses / Additional Payments",
    "cat_co_people_employee_zus": "Employee ZUS",
    "cat_co_people_employee_pit": "Employee PIT",
    "cat_co_people_contractors": "Contractors",
    "cat_co_taxes_vat": "VAT Payments",
    "cat_co_taxes_income_tax": "Income Tax",
    "cat_co_taxes_owner_zus": "Owner ZUS",
    "cat_co_services_accountant": "Accountant",
    "cat_co_services_software": "Software / SaaS",
    "cat_co_services_other": "Other Services",
    "cat_co_financial_bank_fees": "Bank Fees",
    "cat_co_financial_loan_repayment": "Loan Repayment",
    "cat_co_financial_stock_exchange": "Stock-Exchange Cash Out",
    "cat_co_financial_other": "Other Financial Costs",
    "cat_co_financial_loan_given": "Loan Given",
    "cat_co_inventory_devices": "Devices for Resale",
    "cat_co_inventory_supplements": "Supplements",
    "cat_co_inventory_accessories": "Accessories",
    "cat_co_capex_machines": "Machines",
    "cat_co_capex_equipment": "Equipment",
    "cat_co_capex_renovation": "Renovation / Improvements",
    "cat_co_training_int_course_fees": "Course Fees",
    "cat_co_training_int_hotel": "Hotel",
    "cat_co_training_int_transport": "Transport",
    "cat_co_training_int_food": "Food / Catering",
    "cat_co_training_int_other": "Other Training Costs",
    "cat_co_training_del_preparation": "Preparation Costs",
    "cat_co_training_del_travel": "Travel",
    "cat_co_training_del_food": "Food / Catering",
    "cat_co_training_del_commissions": "Commissions",
    "cat_co_private_withdrawals": "Private Withdrawals",
    "cat_co_other_expense": "Other Expense",
}

VALIDATION_ERRORS = {
    "Date is required.": "Date is required.",
    "Date must be a valid YYYY-MM-DD value.": "Date must be a valid YYYY-MM-DD value.",
    "Direction must be cash_in or cash_out.": "Direction must be cash_in or cash_out.",
    "Amount must be a positive number.": "Amount must be a positive number.",
    "Amount must be greater than 0.": "Amount must be greater than 0.",
    "Category must be a valid category id.": "Category must be a valid category id.",
    "Payment method must be cash, card, or transfer.": (
        "Payment method must be cash, card, or transfer."
    ),
    "VAT rate must be one of 0, 5, 8, or 23.": (
        "VAT rate must be one of 0, 5, 8, or 23."
    ),
    "Cash-in type is required for cash_in transactions.": (
        "Cash-in type is required for cash_in transactions."
    ),
    "Cash-in type must be internal or external.": (
        "Cash-in type must be internal or external."
    ),
    "VAT deductible percentage must be empty for cash_in transactions.": (
        "VAT deductible percentage must be empty for cash_in transactions."
    ),
    "Cash-in type must be empty for cash_out transactions.": (
        "Cash-in type must be empty for cash_out transactions."
    ),
    "VAT deductible percentage is required for cash_out transactions.": (
        "VAT deductible percentage is required for cash_out transactions."
    ),
    "VAT deductible percentage must be one of 0, 50, or 100.": (
        "VAT deductible percentage must be one of 0, 50, or 100."
    ),
    "Internal cash_in must use a VAT rate of 0.": (
        "Internal cash_in must use a VAT rate of 0."
    ),
    "Internal cash_in must use cash as payment method.": (
        "Internal cash_in must use cash as payment method."
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
    "Company is required.": "Company is required.",
    "Company must be a valid active company.": "Company must be a valid active company.",
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
