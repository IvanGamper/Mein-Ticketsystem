#DATABASE.py
import os
import pymysql

DB_KONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Xyz1343!!!"),
    "database": os.getenv("DB_NAME", "ticketsystemabkoo13"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
}

class DBVerbindung:
    """Kontextmanager für DB-Verbindung (Commit / Rollback automatisch)."""

    def __init__(self, konfig: dict = DB_KONFIG):
        self.konfig = konfig
        self.conn = None

    def __enter__(self):
        self.conn = pymysql.connect(**self.konfig)
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()

def daten_abfragen(sql: str, params: tuple = ()):
    """Führt SELECT-Query aus und liefert alle Zeilen als Liste von Dicts."""
    with DBVerbindung() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)

            return cur.fetchall()

def query_ausfuehren(sql: str, params: tuple = ()):
    """Führt INSERT/UPDATE/DELETE aus. Gibt ggf. lastrowid zurück."""
    with DBVerbindung() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)

            return getattr(cur, "lastrowid", 0) or 0