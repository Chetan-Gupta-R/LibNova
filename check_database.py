
from database import initialize_database, get_connection, DB_PATH

initialize_database()

with get_connection() as conn:
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

print("Database:", DB_PATH)
print("Tables created:")
for table in tables:
    print("-", table["name"])
