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
                    '"owner_id" INTEGER NOT NULL, "valid_since" INTEGER);')
        cur.execute('CREATE TABLE IF NOT EXISTS "event" ("id" INTEGER PRIMARY KEY, "badge_hex" TEXT NOT NULL, '
                    '"time" INTEGER NOT NULL, "source_id" INTEGER NOT NULL);')
        cur.close()
        self.conn.commit()

    def log_event(self, timestamp: int, badge: str, source: str):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "source" WHERE "name" = ?', (source,))
        result = cur.fetchone()
        if result is None:
            cur.execute('INSERT INTO "source" ("name") VALUES (?)', (source,))
            cur.execute('SELECT last_insert_rowid()')
            result = cur.fetchone()
        source_id = result[0]
        cur.execute('INSERT INTO event (badge_hex, time, source_id) VALUES (?, ?, ?)', (badge, timestamp, source_id))
        cur.close()
        self.conn.commit()

    def get_owner_id_by_nme(self, name: str):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "owner" WHERE "name" = ?', (name,))
        result = cur.fetchone()
        if result is not None:
            existing_id = result[0]
            return existing_id
        cur.execute('INSERT INTO "owner" ("name") VALUES (?)', (name,))
        cur.execute('SELECT last_insert_rowid()')
        result = cur.fetchone()
        new_id = result[0]
        return new_id

    def add_badge_by_owner_id(self, badge_hex: str, owner_id: int, valid_since: int = None):
        cur = self.conn.cursor()
        if valid_since is None:
            valid_since = QDateTime.currentDateTime().toSecsSinceEpoch()
        cur.execute('INSERT INTO "badge" ("owner_id", "badge_hex", "valid_since") VALUES (?, ?, ?)',
                    (owner_id, badge_hex, valid_since))
        cur.execute('SELECT last_insert_rowid()')
        result = cur.fetchone()
        new_id = result[0]
        return new_id

    def add_badge_by_name(self, badge_hex: str, owner: str, valid_since: int = None):
        owner_id = self.get_owner_id_by_nme(owner)
        new_id = self.add_badge_by_owner_id(badge_hex, owner_id, valid_since)
        return new_id

    def get_events_between_timestamps(self, time_from: int, time_to: int):
        cur = self.conn.cursor()
        cur.execute('SELECT owner.name, event.time, badge.badge_hex FROM owner, event, badge '
                    'WHERE owner.id = badge.owner_id AND event.badge_hex = badge.badge_hex '
                    'AND event.time >= ? AND event.time <= ?;', (time_from, time_to))
        result = cur.fetchall()
        table = []
        for record in result:
            name = record[0]
            timestamp = record[1]
            badge = record[2]
            time_obj = QDateTime.fromSecsSinceEpoch(timestamp)
            date_str = time_obj.toString('dd.MM.yyyy')
            time_str = time_obj.toString('hh:mm:ss')
            table.append((date_str, time_str, name, badge))
        return table
