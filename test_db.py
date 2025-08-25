import os
from dotenv import load_dotenv
import pymysql

# 🔽 Explicit full path to your .env file
env_path = r"D:\pro2\Attendance Management System using Face Recognition\ .env"

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Read environment variables
host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DB")

# Debug print
print("Loaded credentials:")
print("HOST:", host)
print("USER:", user)
print("PASS:", "(hidden)" if password else None)
print("DB:", database)

# Check if all variables are loaded
if not all([host, user, password, database]):
    print("❌ One or more environment variables are missing. Check your .env file.")
    exit()

# Try connecting to MySQL
try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    print("✅ Successfully connected to the MySQL database!")
    connection.close()
except pymysql.MySQLError as e:
    print("❌ Connection failed:", e)
