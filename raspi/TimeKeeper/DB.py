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
        cur.execute('CREATE TABLE IF NOT EXISTS "badge" ("id" INTEGER PRIMARY KEY, "hex" TEXT NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS "badge_owner" ("id" INTEGER  PRIMARY KEY, "owner_id" INTEGER NOT NULL, '
                    '"badge_id" INTEGER NOT NULL, "valid_since" INTEGER NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS "event" ("id" INTEGER PRIMARY KEY, "badge_id" INTEGER NOT NULL, '
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
        self.conn.commit()
        return source_id

    def get_badge_id(self, badge_hex: str):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "badge" WHERE "hex" = ?;', (badge_hex, ))
        result = cur.fetchone()
        if result:
            badge_id = result[0]
        else:
            cur.execute('INSERT INTO "badge" ("hex") VALUES (?);', (badge_hex, ))
            cur.execute('SELECT last_insert_rowid()')
            result = cur.fetchone()
            badge_id = result[0]
        cur.close()
        self.conn.commit()
        return badge_id

    def event_exists(self, timestamp: int, badge_id: int):
        cur = self.conn.cursor()
        cur.execute('SELECT "id" FROM "event" WHERE "badge_id" =  ? '
                    'AND "event"."time" = ?', (badge_id, timestamp))
        result = cur.fetchone()
        cur.close()
        if result:
            return True
        else:
            return False

    def log_event(self, timestamp: int, badge_hex: str, source: str):
        source_id = self.get_source_id(source)
        badge_id = self.get_badge_id(badge_hex)
        if not self.event_exists(timestamp, badge_id):
            cur = self.conn.cursor()
            cur.execute('INSERT INTO event (badge_id, time, source_id) VALUES (?, ?, ?)',
                        (badge_id, timestamp, source_id))
            cur.close()
            self.conn.commit()

    def get_owner_id_by_name(self, name: str):
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

    def add_badge_by_owner_id(self, badge_id: int, owner_id: int, valid_since: int = None):
        if valid_since is None:
            valid_since = QDateTime.currentDateTime().toSecsSinceEpoch()

        valid_owner_id = self.get_valid_owner_id(badge_id, valid_since)

        # Only add a new owner if not already valid
        if valid_owner_id != owner_id:
            cur = self.conn.cursor()
            cur.execute('INSERT INTO "badge_owner" ("owner_id", "badge_id", "valid_since") VALUES (?, ?, ?)',
                        (owner_id, badge_id, valid_since))
            cur.close()
            self.conn.commit()

    def add_badge_by_name(self, badge_hex: str, owner: str, valid_since: int = None):
        owner_id = self.get_owner_id_by_name(owner)
        badge_id = self.get_badge_id(badge_hex)
        self.add_badge_by_owner_id(badge_id, owner_id, valid_since)

    def get_valid_owner_id(self, badge_id: int, valid_since: int):
        cur = self.conn.cursor()
        cur.execute('SELECT "owner_id" FROM "badge_owner" '
                    'WHERE "badge_id" = ? AND "valid_since" = ? '
                    'ORDER BY "valid_since" DESC LIMIT 1;', (badge_id, valid_since))
        result = cur.fetchone()
        cur.close()
        if result:
            owner_id = result[0]
            return owner_id
        else:
            return None

    def get_valid_badge_owner(self, badge_hex: str, time: int = 0):
        cur = self.conn.cursor()
        cur.execute('SELECT "owner"."name" FROM "owner", "badge", "badge_owner" '
                    'WHERE "owner"."id" = "badge_owner"."owner_id" AND "badge"."id" = "badge_owner"."badge_id" '
                    'AND "badge"."hex" = ? AND "badge_owner"."valid_since" <= ? '
                    'ORDER BY "badge_owner"."valid_since" DESC;', (badge_hex, time))
        result = cur.fetchone()
        cur.close()

        if result:
            owner_name = result[0]
            return owner_name
        else:
            return badge_hex

    def get_badge_owner_by_id(self, badge_id: int, valid_since: int = None):
        if valid_since is None:
            valid_since = QDateTime.currentDateTime().toSecsSinceEpoch()
        cur = self.conn.cursor()
        cur.execute('SELECT "owner"."name" FROM "owner", "badge_owner" '
                    'WHERE "badge_owner"."owner_id" = "owner"."id" '
                    'AND "badge_owner"."badge_id" = ? AND "badge_owner"."valid_since" <= ? '
                    'ORDER BY "badge_owner"."valid_since" DESC LIMIT 1;', (badge_id, valid_since))
        result = cur.fetchone()
        cur.close()
        if result:
            name = result[0]
            return name
        else:
            return None

    def get_events_between_timestamps(self, time_from: int, time_to: int):
        cur = self.conn.cursor()
        cur.execute('SELECT "event"."time", "badge"."hex" FROM "event", "badge" '
                    'WHERE "event"."badge_id" = "badge"."id" '
                    'AND "event"."time" >= ? AND "event"."time" <= ? '
                    'ORDER BY "event"."time";', (time_from, time_to))
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
        cur.execute('SELECT "id", "hex" FROM "badge" ORDER BY "hex"')
        result = cur.fetchall()
        cur.close()

        owners = []
        for record in result:
            badge_id = record[0]
            badge_hex = record[1]
            owner_name = self.get_badge_owner_by_id(badge_id)
            if owner_name:
                owners.append(f'{badge_hex} {owner_name}')
            else:
                owners.append(badge_hex)

        return owners

    @pyqtSlot(NetRequest)
    def answer_net_request(self, request: NetRequest):
        if request.type == 'events':
            result = self.get_events_between_timestamps(request.params[0], request.params[1])
            lines = []
            for element in result:
                lines.append('\t'.join(element))
            text_block = '\n'.join(lines) + '\n'
            request.answer(text_block)
        elif request.type == 'owners':
            result = self.get_owners()
            text_block = '\n'.join(result) + '\n'
            request.answer(text_block)
        elif request.type == 'set owner':
            badge_hex = request.params[0]
            name = request.params[1]
            valid_since = request.params[2]
            self.add_badge_by_name(badge_hex, name, valid_since)
            request.deleteLater()
        else:
            request.deleteLater()

