# Placeholder for SQLite setup
# This file can contain database connection utilities or schema definitions if needed,
# though basic initialization is in ChatHistoryManager.

import sqlite3
from .settings import DATABASE_PATH # Import from sibling settings.py

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

# Example usage (though ChatHistoryManager handles its own connections):
# def query_db(query, args=(), one=False):
#     conn = get_db_connection()
#     cur = conn.execute(query, args)
#     rv = cur.fetchall()
#     conn.close()
#     return (rv[0] if rv else None) if one else rv