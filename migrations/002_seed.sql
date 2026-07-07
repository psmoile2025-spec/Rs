-- Default admin user is created automatically by the app factory on first run.
-- See app/__init__.py _init_default_admin().

-- Sample categories
INSERT INTO categories (name, sort_order) VALUES
    ('Appetizers', 1),
    ('Main Course', 2),
    ('Desserts', 3),
    ('Beverages', 4)
ON CONFLICT (name) DO NOTHING;

-- Sample menu items (assumes categories above got IDs in order)
-- Note: These inserts reference category names via subquery for portability
INSERT INTO menu_items (category_id, name, description, price, cost, available)
SELECT id, 'Spring Rolls', 'Crispy vegetable spring rolls', 6.99, 3.50, TRUE FROM categories WHERE name = 'Appetizers'
UNION ALL
SELECT id, 'Garlic Bread', 'Toasted bread with garlic butter', 4.99, 2.00, TRUE FROM categories WHERE name = 'Appetizers'
UNION ALL
SELECT id, 'Grilled Chicken', 'Marinated chicken breast with herbs', 14.99, 7.50, TRUE FROM categories WHERE name = 'Main Course'
UNION ALL
SELECT id, 'Beef Steak', '8oz ribeye with mashed potatoes', 22.99, 12.00, TRUE FROM categories WHERE name = 'Main Course'
UNION ALL
SELECT id, 'Pasta Alfredo', 'Creamy fettuccine alfredo', 12.99, 6.00, TRUE FROM categories WHERE name = 'Main Course'
UNION ALL
SELECT id, 'Chocolate Cake', 'Rich dark chocolate layer cake', 7.99, 3.00, TRUE FROM categories WHERE name = 'Desserts'
UNION ALL
SELECT id, 'Ice Cream', 'Vanilla bean ice cream (2 scoops)', 4.99, 1.50, TRUE FROM categories WHERE name = 'Desserts'
UNION ALL
SELECT id, 'Cola', 'Refreshing cola drink', 2.49, 1.00, TRUE FROM categories WHERE name = 'Beverages'
UNION ALL
SELECT id, 'Orange Juice', 'Freshly squeezed orange juice', 3.49, 1.50, TRUE FROM categories WHERE name = 'Beverages'
UNION ALL
SELECT id, 'Coffee', 'Fresh brewed coffee', 2.99, 0.75, TRUE FROM categories WHERE name = 'Beverages';
