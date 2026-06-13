-- Reference schema for the experiment report.
-- The FastAPI backend creates these tables automatically on startup.

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(64) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    current_stock INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    status VARCHAR(16) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(40) NOT NULL UNIQUE,
    customer_name VARCHAR(80) NOT NULL,
    status VARCHAR(16) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    order_time TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    line_total NUMERIC(12, 2) NOT NULL
);
