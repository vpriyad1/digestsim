# db_connect.py
# Provides a function to connect to the digestsim MySQL database.

import mysql.connector
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        ssl_disabled=True
    )
    return conn
