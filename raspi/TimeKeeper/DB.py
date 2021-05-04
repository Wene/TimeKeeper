#!/usr/bin/env python3

from PyQt5.QtCore import *
import sqlite3


class DB(QObject):
    def __init__(self, parent, db_file: str):
        super().__init__(parent)
        self.conn = sqlite3.connect(db_file)
        self._create_db()

    def __del__(self):
        self.conn.close()

    def _create_db(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS "owner" ("id" INTEGER PRIMARY KEY, "name" TEXT NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS "source" ("id" INTEGER PRIMARY KEY, "name" TEXT NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS "badge" ("id" INTEGER PRIMARY KEY, "badge_hex" TEXT NOT NULL, '
                    '"owner_id" INTEGER NOT NULL, "valid_since" INTEGER, "valid_until" INTEGER);')
        cur.execute('CREATE TABLE IF NOT EXISTS "event" ("id" INTEGER PRIMARY KEY, "badge_hex" TEXT NOT NULL, '
                    '"time" INTEGER NOT NULL, "source_id" INTEGER NOT NULL);')
        cur.close()
        self.conn.commit()

    def log_event(self, timestamp: int, badge: str, source: str):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "source" WHERE "name" = ?', (source,))
        result = cur.fetchone()
        if result is None:
            cur.execute('INSERT INTO source (name) VALUES (?)', (source,))
            cur.execute('SELECT last_insert_rowid()')
            result = cur.fetchone()
        source_id = result[0]
        cur.execute('INSERT INTO event (badge_hex, time, source_id) VALUES (?, ?, ?)', (badge, timestamp, source_id))
        cur.close()
        self.conn.commit()

