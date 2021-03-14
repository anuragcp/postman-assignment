# /app/config/__init__.py

import os

class DatabaseConf():
    def __init__(self):
        try:
            self.database_name = os.environ['DATABASE_NAME']
            self.database_user = os.environ['DATABASE_USER']
            self.database_password = os.environ['DATABASE_PASSWORD']
            self.database_host = os.environ['DATABASE_HOST']
            self.database_port = os.environ['DATABASE_PORT']
        except KeyError:
            # default value if environment values are not provided
            self.database_name = 'postman'
            self.database_user = 'postgres'
            self.database_password = 'postgres'
            self.database_host = '127.0.0.1'
            self.database_port = '5432'
        finally:
            self.wrap_and_return()

    def wrap_and_return(self):
        return {
            'database_name' : self.database_name,
            'database_user' : self.database_user,
            'database_password' : self.database_password,
            'database_host' : self.database_host,
            'database_port' : self.database_port
        }