import sqlite3
from datetime import datetime

def setup_database(db_name="ecommerce.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Foreign keys support enable karna
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Customers Table (8 Columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        signup_date DATE NOT NULL,
        loyalty_tier TEXT NOT NULL,       -- Bronze, Silver, Gold, Platinum
        loyalty_points INTEGER DEFAULT 0
    );
    """)

    # 2. Products Table (8 Columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL,
        cost_price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        rating REAL DEFAULT 0.0,
        is_active INTEGER DEFAULT 1       -- 1 for Active, 0 for Discontinued
    );
    """)

    # 3. Orders Table (8 Columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATETIME NOT NULL,
        order_status TEXT NOT NULL,       -- Completed, Pending, Cancelled, Returned
        shipping_city TEXT NOT NULL,
        shipping_fee REAL DEFAULT 0.0,
        discount_amount REAL DEFAULT 0.0,
        total_amount REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );
    """)

    # 4. Order Items Table (7 Columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price_at_sale REAL NOT NULL,
        discount_applied REAL DEFAULT 0.0,
        line_total REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    );
    """)

    # 5. Payments Table (7 Columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_method TEXT NOT NULL,     -- Credit Card, EasyPaisa, JazzCash, Bank Transfer, COD
        transaction_reference TEXT UNIQUE NOT NULL,
        amount_paid REAL NOT NULL,
        payment_status TEXT NOT NULL,     -- Success, Failed, Refunded
        payment_date DATETIME NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
    );
    """)

    # ----------------------------------------------------
    # Seed Realistic Sample Data
    # ----------------------------------------------------
    
    # Insert Customers (8 cols)
    customers_data = [
        ('Ali Khan', 'ali.khan@gmail.com', 'Karachi', 'Pakistan', '2025-01-15', 'Platinum', 1250),
        ('Sara Ahmed', 'sara.ahmed@yahoo.com', 'Lahore', 'Pakistan', '2025-02-10', 'Gold', 850),
        ('Hamza Tariq', 'hamza.t@outlook.com', 'Islamabad', 'Pakistan', '2025-03-01', 'Silver', 420),
        ('Ayesha Malik', 'ayesha.m@gmail.com', 'Karachi', 'Pakistan', '2025-03-12', 'Bronze', 110),
        ('Usman Raza', 'usman.raza@hotmail.com', 'Faisalabad', 'Pakistan', '2025-04-05', 'Gold', 790),
        ('Zainab Fatima', 'zainab.f@gmail.com', 'Rawalpindi', 'Pakistan', '2025-04-18', 'Platinum', 1600),
        ('Bilal Siddiqui', 'bilal.s@yahoo.com', 'Karachi', 'Pakistan', '2025-05-02', 'Silver', 350)
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO customers (full_name, email, city, country, signup_date, loyalty_tier, loyalty_points)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, customers_data)

    # Insert Products (8 cols)
    products_data = [
        ('Mechanical Gaming Keyboard', 'Electronics', 85.0, 50.0, 45, 4.8, 1),
        ('Wireless Ergonomic Mouse', 'Electronics', 45.0, 25.0, 80, 4.6, 1),
        ('Noise Cancelling Headphones', 'Audio', 180.0, 110.0, 25, 4.9, 1),
        ('4K Ultra HD Monitor 27-inch', 'Electronics', 320.0, 220.0, 15, 4.7, 1),
        ('Ergonomic Office Chair', 'Furniture', 210.0, 140.0, 10, 4.4, 1),
        ('USB-C Fast Charging Hub', 'Accessories', 35.0, 15.0, 120, 4.3, 1),
        ('Standing Desk Mat', 'Accessories', 28.0, 12.0, 60, 4.1, 1),
        ('Discontinued Smart Watch v1', 'Wearables', 99.0, 60.0, 0, 3.8, 0)
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO products (product_name, category, unit_price, cost_price, stock_quantity, rating, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, products_data)

    # Insert Orders (8 cols)
    orders_data = [
        (1, '2026-06-01 10:30:00', 'Completed', 'Karachi', 10.0, 0.0, 215.0),
        (2, '2026-06-05 14:15:00', 'Completed', 'Lahore', 15.0, 20.0, 315.0),
        (1, '2026-06-12 18:45:00', 'Completed', 'Karachi', 0.0, 15.0, 180.0),
        (3, '2026-06-20 09:10:00', 'Cancelled', 'Islamabad', 10.0, 0.0, 45.0),
        (4, '2026-07-02 11:20:00', 'Completed', 'Karachi', 10.0, 5.0, 75.0),
        (5, '2026-07-15 16:50:00', 'Completed', 'Faisalabad', 20.0, 10.0, 220.0),
        (6, '2026-07-28 20:05:00', 'Completed', 'Rawalpindi', 0.0, 30.0, 500.0),
        (7, '2026-08-01 13:40:00', 'Pending', 'Karachi', 10.0, 0.0, 120.0),
        (2, '2026-08-03 15:25:00', 'Completed', 'Lahore', 10.0, 0.0, 85.0),
        (6, '2026-08-10 19:10:00', 'Completed', 'Rawalpindi', 15.0, 25.0, 360.0)
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO orders (customer_id, order_date, order_status, shipping_city, shipping_fee, discount_amount, total_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, orders_data)

    # Insert Order Items (7 cols)
    order_items_data = [
        (1, 1, 1, 85.0, 0.0, 85.0),
        (1, 3, 1, 130.0, 0.0, 130.0),
        (2, 4, 1, 320.0, 20.0, 300.0),
        (3, 3, 1, 180.0, 0.0, 180.0),
        (4, 2, 1, 45.0, 0.0, 45.0),
        (5, 6, 2, 35.0, 0.0, 70.0),
        (6, 5, 1, 210.0, 0.0, 210.0),
        (7, 4, 1, 320.0, 0.0, 320.0),
        (7, 3, 1, 180.0, 0.0, 180.0),
        (8, 1, 1, 85.0, 0.0, 85.0),
        (8, 6, 1, 35.0, 0.0, 35.0),
        (9, 1, 1, 85.0, 0.0, 85.0),
        (10, 4, 1, 320.0, 0.0, 320.0),
        (10, 2, 1, 45.0, 0.0, 45.0)
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price_at_sale, discount_applied, line_total)
    VALUES (?, ?, ?, ?, ?, ?);
    """, order_items_data)

    # Insert Payments (7 cols)
    payments_data = [
        (1, 'Credit Card', 'TXN-908123', 215.0, 'Success', '2026-06-01 10:35:00'),
        (2, 'Bank Transfer', 'TXN-908124', 315.0, 'Success', '2026-06-05 14:20:00'),
        (3, 'JazzCash', 'TXN-908125', 180.0, 'Success', '2026-06-12 18:50:00'),
        (4, 'EasyPaisa', 'TXN-908126', 45.0, 'Refunded', '2026-06-20 09:15:00'),
        (5, 'COD', 'TXN-908127', 75.0, 'Success', '2026-07-04 12:00:00'),
        (6, 'Credit Card', 'TXN-908128', 220.0, 'Success', '2026-07-15 16:55:00'),
        (7, 'Credit Card', 'TXN-908129', 500.0, 'Success', '2026-07-28 20:10:00'),
        (8, 'EasyPaisa', 'TXN-908130', 120.0, 'Success', '2026-08-01 13:45:00'),
        (9, 'JazzCash', 'TXN-908131', 85.0, 'Success', '2026-08-03 15:30:00'),
        (10, 'Bank Transfer', 'TXN-908132', 360.0, 'Success', '2026-08-10 19:15:00')
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO payments (order_id, payment_method, transaction_reference, amount_paid, payment_status, payment_date)
    VALUES (?, ?, ?, ?, ?, ?);
    """, payments_data)

    conn.commit()
    conn.close()
    print("Database `ecommerce.db` successfully created with 5 tables and rich dummy data!")

if __name__ == "__main__":
    setup_database()