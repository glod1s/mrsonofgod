import sqlite3


class SQ:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_noref(self):
        with self.connection:
            return self.cursor.execute('SELECT `link` FROM alilinks WHERE referral = ?', (False,)).fetchall()

    def check_noref(self, link):
        with self.connection:
            result = self.cursor.execute("SELECT `referral` FROM `alilinks` WHERE `link` = ?", (link,)).fetchone()
            return result

    def get_textid(self, link):
        with self.connection:
            return self.connection.execute("SELECT `text`, `msgid` FROM alilinks WHERE `link` = ?", (link,)).fetchone()

    def get_textid1(self, link):
        with self.connection:
            return self.connection.execute("SELECT `text`, `msgid` FROM alilinks WHERE `referral` = ?", (link,)).fetchone()

    def update(self, text, link):
        with self.connection:
            return self.cursor.execute('UPDATE `alilinks` SET `text` = ?, referral = ? WHERE `link`=?', (text, True, link,))

    def link_exists(self, link):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `alilinks` WHERE `link` = ?", (link,)).fetchall()
            return result

    def link_exists1(self, link):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `alilinks` WHERE `referral` = ?", (link,)).fetchall()
            return result