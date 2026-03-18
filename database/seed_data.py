from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# 1. CREATE TABLES (Agar file delete kar di ho toh ye zaroori hai)
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT,
    area TEXT,
    rating REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT,
    price REAL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    item_name TEXT,
    price REAL,
    quantity INTEGER
)
""")

# 2. CLEAR OLD DATA
cursor.execute("DELETE FROM menu")
cursor.execute("DELETE FROM restaurants")
cursor.execute("DELETE FROM cart")

# 3. INSERT RESTAURANTS (Using Unique Names to avoid AI Hallucinations)
restaurants = [
    (1, "Pizza Planet",     "Lucknow", 4.2),
    (2, "Burger Byte",      "Delhi",   4.8),
    (3, "The Chicken Hub",  "Lucknow", 4.2),
    (4, "Green Bowl",       "Mumbai",  4.5),
    (5, "Spicy Treat",      "Delhi",   3.9),
]

cursor.executemany(
    "INSERT OR IGNORE INTO restaurants (id, name, area, rating) VALUES (?, ?, ?, ?)",
    restaurants
)

# 4. INSERT MENU ITEMS
menu_items = [
    (1, "Margherita Pizza", 149.0),
    (1, "Pepperoni Pizza",  199.0),
    (1, "Garlic Bread",      79.0),
    (2, "Byte Burger",      189.0),
    (2, "Onion Rings",       79.0),
    (3, "Zinger Burger",    179.0),
    (3, "Popcorn Chicken",  139.0),
    (3, "Pepsi",             49.0),
    (4, "Paneer Wrap",      159.0),
    (5, "Butter Chicken",   199.0),
    (5, "Biryani",          179.0)
]

cursor.executemany(
    "INSERT INTO menu (restaurant_id, item_name, price) VALUES (?, ?, ?)",
    menu_items
)

conn.commit()
conn.close()

print("✅ Database Seeded Successfully with Unique Names!")