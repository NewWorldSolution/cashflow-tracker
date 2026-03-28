INSERT INTO companies (id, name, slug)
VALUES
    (1, 'sp', 'sp'),
    (2, 'ltd', 'ltd'),
    (3, 'ff', 'ff'),
    (4, 'private', 'private')
ON CONFLICT DO NOTHING;
