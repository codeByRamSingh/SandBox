import psycopg2
from psycopg2 import Error

print ("Individual Entry")

try:
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
    print("Database connection successful.")
    connection = conn.cursor()

    # Create table if not exists
    connection.execute("""
    CREATE TABLE IF NOT EXISTS individuals (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        phone VARCHAR(20),
        email VARCHAR(100)
    )
    """)

    # Insert data
    connection.execute("""
    INSERT INTO individuals (first_name, last_name, phone, email)
    VALUES (%s, %s, %s, %s)
    """, (first_name, last_name, phone, email))

    conn.commit()
    connection.close()
    conn.close()

    print("Data saved to individuals table.")
except Error as e:
    print(f"Error connecting to database: {e}")