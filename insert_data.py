import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("swiggy.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT,
    area TEXT,
    rating REAL
)
""")

# Insert sample data
restaurants = [
    (1, "Pizza Hut", "Lucknow", 4.2),
    (2, "Burger King", "Delhi", 4.0),
    (3, "KFC", "Lucknow", 4.1),
    (4, "Green Bowl", "Mumbai", 4.5),
    (5, "Spicy Treat", "Delhi", 3.9),
]

cursor.executemany(
    "INSERT OR REPLACE INTO restaurants VALUES (?, ?, ?, ?)",
    restaurants
)

conn.commit()
conn.close()

print("✅ Data inserted successfully!")