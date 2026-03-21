-- Income categories
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (1,  'services',          'Services',            'income',  23, NULL),
    (2,  'products',          'Products sold',        'income',  23, NULL),
    (3,  'internal_transfer', 'Internal transfer',    'income',   0, NULL),
    (4,  'other_income',      'Other income',         'income',  23, NULL);

-- Expense categories
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (5,  'marketing',            'Marketing & advertising',    'expense', 23, 100),
    (6,  'marketing_commission', 'Sales commissions',          'expense', 23, 100),
    (7,  'rent',                 'Rent & premises',            'expense', 23, 100),
    (8,  'utilities',            'Utilities',                  'expense', 23, 100),
    (9,  'renovation',           'Renovation & repairs',       'expense', 23, 100),
    (10, 'office_supplies',      'Office supplies',            'expense', 23, 100),
    (11, 'cleaning',             'Cleaning services',          'expense',  0,   0),
    (12, 'consumables',          'Operational consumables',    'expense', 23, 100),
    (13, 'equipment',            'Equipment & tools',          'expense', 23, 100),
    (14, 'contractor_fees',      'Contractor & educator fees', 'expense', 23, 100),
    (15, 'taxes',                'Taxes & ZUS',                'expense',  0,   0),
    (16, 'it_software',          'IT & software',              'expense', 23, 100),
    (17, 'salaries',             'Salaries & employee costs',  'expense',  0,   0),
    (18, 'transport_vehicle',    'Vehicle & petrol',           'expense', 23,  50),
    (19, 'transport_travel',     'Travel & transport',         'expense',  0, 100),
    (20, 'training',             'Training & education',       'expense', 23, 100),
    (21, 'inventory',            'Inventory purchases',        'expense', 23, 100),
    (22, 'other_expense',        'Other expense',              'expense', 23, 100);
