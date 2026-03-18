from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# 1. Restaurants Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    area TEXT NOT NULL,
    rating REAL
)
""")

# 2. Menu Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
)
""")

# 3. Cart Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    quantity INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
)
""")

# 4. Orders Table (FIXED: Added checkout columns)
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT NOT NULL,
    price REAL,
    quantity INTEGER,
    address TEXT,
    phone TEXT,
    payment_method TEXT,
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ Tables created successfully with Checkout columns!")