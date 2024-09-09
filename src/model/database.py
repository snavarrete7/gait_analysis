from sqlalchemy import create_engine, text, Table, MetaData

class Database():
    def __init__(self):
        self.db_config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': 3306,
            'database': 'rtanalysis'
        }
        self.engine = create_engine('mysql+pymysql://root:@localhost/rtanalysis')