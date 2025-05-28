print ("Hello world");

import psycopg2

# Collect user input
first_name = input("Enter first name: ")
last_name = input("Enter last name: ")
phone = input("Enter phone: ")
email = input("Enter email address: ")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="sandbox",
    user="postgres",
    password="Adi@1989"
)
db = conn.cursor()

# Create table if not exists
db.execute("""
CREATE TABLE IF NOT EXISTS individuals (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100)
)
""")

# Insert data
db.execute("""
INSERT INTO individuals (first_name, last_name, phone, email)
VALUES (%s, %s, %s, %s)
""", (first_name, last_name, phone, email))

conn.commit()
db.close()
conn.close()

print("Data saved to individuals table.")