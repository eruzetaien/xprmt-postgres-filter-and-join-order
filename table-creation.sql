DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;


CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    customer_tier TEXT,
    signup_date DATE
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price NUMERIC(12,0)
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT,
    order_date TIMESTAMP,
    status TEXT
);

CREATE TABLE order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price NUMERIC(12,0)
);