#!/usr/bin/env python3

from PyQt5.QtCore import *
from .Server import NetRequest
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

    def get_source_id(self, source: str):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "source" WHERE "name" = ?', (source,))
        result = cur.fetchone()
        if result is None:
            cur.execute('INSERT INTO "source" ("name") VALUES (?)', (source,))
            cur.execute('SELECT last_insert_rowid()')
            result = cur.fetchone()
        source_id = result[0]
        cur.close()
        return source_id

    def event_exists(self, timestamp: int, badge: str):
        existing = False
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM event WHERE badge_hex = ? AND time = ?', (badge, timestamp))
        result = cur.fetchone()
        if result:
            existing = True
        cur.close()
        return existing

    def log_event(self, timestamp: int, badge: str, source: str):
        source_id = self.get_source_id(source)
        if not self.event_exists(timestamp, badge):
            cur = self.conn.cursor()
            cur.execute('INSERT INTO event (badge_hex, time, source_id) VALUES (?, ?, ?)',
                        (badge, timestamp, source_id))
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
        cur.close()
        self.conn.commit()
        return new_id

    def add_badge_by_owner_id(self, badge_hex: str, owner_id: int, valid_since: int = None):
        cur = self.conn.cursor()
        if valid_since is None:
            valid_since = QDateTime.currentDateTime().toSecsSinceEpoch()

        # Check for existing, still valid badge
        cur.execute('SELECT "id" from "badge" '
                    'WHERE "badge_hex" = ? AND "owner_id" = ? AND "valid_since" <= ? '
                    'ORDER BY "valid_since" DESC '
                    'LIMIT 1;', (badge_hex, owner_id, valid_since))
        result = cur.fetchall()

        # Only add a new owner if not already valid
        if not result:
            cur.execute('INSERT INTO "badge" ("owner_id", "badge_hex", "valid_since") VALUES (?, ?, ?)',
                        (owner_id, badge_hex, valid_since))
        cur.close()
        self.conn.commit()

    def add_badge_by_name(self, badge_hex: str, owner: str, valid_since: int = None):
        owner_id = self.get_owner_id_by_nme(owner)
        self.add_badge_by_owner_id(badge_hex, owner_id, valid_since)

    def get_valid_badge_owner(self, badge_hex: str, time: int = 0):
        cur = self.conn.cursor()
        cur.execute('SELECT owner.name FROM owner, badge '
                    'WHERE owner.id = badge.owner_id AND badge.badge_hex = ? AND badge.valid_since <= ? '
                    'ORDER BY badge.valid_since DESC;', (badge_hex, time))
        result = cur.fetchone()
        cur.close()

        if result:
            owner_name = result[0]
            return owner_name
        else:
            return badge_hex

    def get_events_between_timestamps(self, time_from: int, time_to: int):
        cur = self.conn.cursor()
        cur.execute('SELECT time, badge_hex FROM event WHERE time >= ? AND time <= ? '
                    'ORDER BY time;', (time_from, time_to))
        result = cur.fetchall()
        cur.close()

        table = []
        for record in result:
            timestamp = record[0]
            badge = record[1]
            name = self.get_valid_badge_owner(badge, timestamp)
            time_obj = QDateTime.fromSecsSinceEpoch(timestamp)
            date_str = time_obj.toString('dd.MM.yyyy')
            time_str = time_obj.toString('hh:mm:ss')
            table.append((date_str, time_str, name))
        return table

    def get_owners(self):
        cur = self.conn.cursor()
        cur.execute('SELECT badge_hex, name FROM ' 
                    '(SELECT * FROM badge, owner WHERE badge.owner_id = owner.id ORDER BY badge.valid_since DESC) '
                    'GROUP BY badge_hex;')
        result = cur.fetchall()
        cur.close()
        table = []
        for record in result:
            badge = record[0]
            name = record[1]
            table.append(f'{badge} {name}')
        return table

    @pyqtSlot(NetRequest)
    def answer_net_request(self, request: NetRequest):
        if request.type == 'events':
            result = self.get_events_between_timestamps(request.params[0], request.params[1])
            lines = []
            for element in result:
                lines.append('\t'.join(element))
            text_block = '\n'.join(lines) + '\n'
            data = QByteArray(text_block.encode())
            request.answer(data)
        elif request.type == 'owners':
            result = self.get_owners()
            text_block = '\n'.join(result) + '\n'
            data = QByteArray(text_block.encode())
            request.answer(data)
        elif request.type == 'set owner':
            badge_hex = request.params[0]
            name = request.params[1]
            valid_since = request.params[2]
            self.add_badge_by_name(badge_hex, name, valid_since)
            request.deleteLater()
        else:
            request.deleteLater()

