TRUNCATE TABLE
    order_items,
    orders,
    products,
    customers
RESTART IDENTITY;

INSERT INTO customers (customer_tier, signup_date)
SELECT
    CASE
        WHEN gs % 10 < 6 THEN 'regular'
        WHEN gs % 10 < 9 THEN 'silver'
        ELSE 'gold'
    END,

    CURRENT_DATE - (gs % 1000)
FROM generate_series(1, 100000) gs;


INSERT INTO orders (customer_id, order_date, status)
SELECT
    (gs % 100000) + 1,

    NOW() - ((gs % 365) || ' days')::INTERVAL,

    CASE
        WHEN gs % 10 < 9 THEN 'completed'
        WHEN gs % 10 = 9 THEN 'pending'
        ELSE 'cancelled'
    END
FROM generate_series(1, 2000000) gs;

INSERT INTO products (product_name, category, price)
SELECT
    'Product ' || gs,

    CASE
        WHEN gs % 10 < 5 THEN 'Electronics'
        WHEN gs % 10 < 8 THEN 'Fashion'
        WHEN gs % 10 < 9 THEN 'Home'
        ELSE 'Books'
    END,

    (10000 + (gs % 5000000))::NUMERIC(12,0)
FROM generate_series(1, 10000) gs;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT
    (gs % 2000000) + 1,
    (gs % 10000) + 1,
    (gs % 5) + 1,
    (10000 + (gs % 5000000))::NUMERIC(12,0)
FROM generate_series(1, 5000000) gs;