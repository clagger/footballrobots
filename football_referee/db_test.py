# Module Imports
import mariadb
import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="server",
        password="password",
        host="192.168.0.100",
        port=3306,
        database="football"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

cur.execute("SELECT * from test")

for (id, name) in cur:
    print(f"ID: {id}, Name: {name} ")

cur.execute(
    "INSERT INTO test (id,name) VALUES (?, ?)",
    (5, "HansPeter"))

conn.close()