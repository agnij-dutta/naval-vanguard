import sqlite3
from datetime import datetime
import json

# Connect to SQLite database (for demo purposes)
conn = sqlite3.connect('reports.db')

# Create the reports table
def init_db():
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            coordinates TEXT,
            significance TEXT,
            timestamp DATETIME
        );
        """)

# Store report in the database
def store_report(report_data):
    with conn:
        for report in report_data:
            conn.execute("""
            INSERT INTO reports (name, type, coordinates, significance, timestamp) 
            VALUES (?, ?, ?, ?, ?);
            """, (report['name'], report['type'], json.dumps(report['coordinates']), report['significance'], datetime.now()))

# Retrieve stored contacts
def get_contacts():
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports")
    rows = cur.fetchall()
    return rows

# Initialize the database
init_db()
