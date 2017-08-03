import sqlite3
import logging

logger = logging.getLogger(__name__)
class db_interface():
    def db_connect(self):
        self.db = sqlite3.connect("position.db")
        self.cursor = self.db.cursor()
        self.db.row_factory = sqlite3.Row

    def db_close(self):
        self.db.close()

    def __init__(self):
        self.db_connect()
        logger.debug('connect to database')

    def select_user_list(self,user_id):
        self.cursor.execute('SELECT * FROM locations WHERE user = ?',(user_id,))
        return self.cursor.fetchall()

    def insert_position(self,dict):
        self.cursor.execute('INSERT INTO locations (user,name,longitude,latitude) VALUES (?,?,?,?)',(dict['user_id'],dict['name'],dict['longitude'],dict['latitude']))
        self.db.commit()
        logger.debug('add a new row into database')

    def select_specific_position(self,l_id):
        self.cursor.execute('SELECT * FROM locations WHERE id = ?',(l_id,))
        return self.cursor.fetchone()

    def delete_specific_position(self,l_id):
        self.cursor.execute('DELETE FROM locations WHERE id = ?',(l_id,))
        self.db.commit()
        logger.debug('delete one row from database')







