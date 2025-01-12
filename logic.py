import sqlite3
from config import DATABASE

timestatuses = [ (_,) for _ in (['Сегодня утром', 'Сегодня днём', 'Сегодня вечером', 'Завтра утром', 'Завтра днём','Завтра вечером','Неограниченный срок','Срочная задача'])]
statuses = [ (_,) for _ in (['Выполнено', 'Частично выполнено', 'Невыполнено'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE tasks (
                            task_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            task_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE timestatuses (
                            timestatus_id INTEGER PRIMARY KEY,
                            timestatus_name TEXT
                        )''')
            conn.execute('''CREATE TABLE task_timestatuses (
                            task_id INTEGER,
                            timestatus_id INTEGER,
                            FOREIGN KEY(task_id) REFERENCES tasks(task_id),
                            FOREIGN KEY(timestatus_id) REFERENCES timestatuses(timestatus_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO timestatuses (timestatus_name) values(?)'
        data = timestatuses
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_task(self, data):
        sql = """INSERT INTO tasks (user_id, task_name, url, status_id) values(?, ?, ?, ?)""" # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [data])


    def insert_timestatus(self, user_id, task_name, timestatus):
        sql = 'SELECT task_id FROM tasks WHERE task_name = ? AND user_id = ?'
        task_id = self.__select_data(sql, (task_name, user_id))[0][0]
        timestatus_id = self.__select_data('SELECT timestatus_id FROM timestatuses WHERE timestatus_name = ?', (timestatus,))[0][0]
        data = [(task_id, timestatus_id)]
        sql = 'INSERT OR IGNORE INTO task_timestatuses VALUES(?, ?)'
        self.__executemany(sql, data)


    def get_statuses(self):
        sql = "SELECT status_name FROM status" # Запиши сюда правильный SQL запрос
        return self.__select_data(sql)
        

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_tasks(self, user_id):
        sql = """SELECT * FROM tasks WHERE user_id = ?""" # Запиши сюда правильный SQL запрос
        return self.__select_data(sql, data = (user_id,))
        
    def get_task_id(self, task_name, user_id):
        return self.__select_data(sql='SELECT task_id FROM tasks WHERE task_name = ? AND user_id = ?  ', data = (task_name, user_id,))[0][0]
        
    def get_timestatuses(self):
        return self.__select_data(sql='SELECT * FROM timestatuses')
    
    def get_task_timestatuses(self, task_name):
        res = self.__select_data(sql='''SELECT timestatus_name FROM tasks 
                                        JOIN task_timestatuses ON tasks.task_id = task_timestatuses.task_id 
                                        JOIN timestatuses ON timestatuses.timestatus_id = task_timestatuses.timestatus_id 
                                        WHERE task_name = ?''', data = (task_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_task_info(self, user_id, task_name):
        sql = """
                                        SELECT task_name, description, url, status_name FROM tasks 
                                        JOIN status ON
                                        status.status_id = tasks.status_id
                                        WHERE task_name=? AND user_id=?
                                        """
        return self.__select_data(sql=sql, data = (task_name, user_id))


    def update_tasks(self, param, data):
        sql = f"""UPDATE tasks SET {param} = ? WHERE task_name = ? AND user_id = ?""" # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [data]) 


    def delete_task(self, user_id, task_id):
        sql = """DELETE FROM tasks WHERE user_id = ? AND task_id = ? """ # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [(user_id, task_id)])
    
    def delete_timestatus(self, task_id, timestatus_id):
        sql = """DELETE FROM timestatuses WHERE timestatus_id = ? AND task_id = ? """ # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [(timestatus_id, task_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)