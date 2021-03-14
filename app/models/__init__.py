# app/models/__init__.py

"""
    This module connects data base by impoerting configurations from 
    config file
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DatabaseConf

class ConnectDB:
    def __init__(self):
        self.conf = DatabaseConf()
        self.connection = None
    
    def initialise(self):
        try:
            print("Connecting to PostgreSQL server")
            self.connection = psycopg2.connect(
                user = self.conf.database_user,
                password = self.conf.database_password,
                host = self.conf.database_host,
                port = self.conf.database_port,
                database = self.conf.database_name
            )
        except Exception as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if self.connection:
                print("Connected to PostgreSQL server")
                return self.connection

        return None

    def terminate(self):
        try:
            if self.connection:
                self.connection.close()
                print("Connection Closed")
        except Exception as error:
            print("Error while terminating to PostgreSQL instance - ", error)


def create_database(drop = True):
    conf = DatabaseConf()
    del conf.database_name
    try:
        print("Connecting to PostgreSQL server")
        connection = psycopg2.connect(
            user = conf.database_user,
            password = conf.database_password,
            host = conf.database_host,
            port = conf.database_port
        )

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        session = connection.cursor()
        # session.execute("SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('postgres');")
        if not drop:
            # not tested yet, need to work on "need not to drop if exists"
            try:
                session.execute('DROP DATABASE IF EXISTS postman')
                connection.commit()
            except Exception as error:
                print("ERROR " + error)
                connection.rollback()
        else:
            try:
                session.execute('DROP DATABASE IF EXISTS postman')
                connection.commit()
            except Exception as e:
                session.execute("""
                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                FROM pg_stat_activity
                                WHERE pg_stat_activity.datname = 'postman' """)
                connection.commit()
                session.execute('DROP DATABASE postman')
                connection.commit()
            try:
                session.execute('CREATE DATABASE postman')
                connection.commit()
            except Exception as error:
                print(f"ERROR: {error}")
                connection.rollback()
            finally:
                session.close()
                connection.close()
                print("INFO: [MODELS] - Database Created.")
                

    except Exception as error:
        print("Error while connecting to PostgreSQL", error)
    

def drop_database():
    try:
        session.execute('DROP DATABASE IF EXISTS postman')
        dbObj.commit()
    except:
        session.execute("""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = 'postman' """)
        session.execute('DROP DATABASE postman')
        dbObj.commit()

def create_airflow_role():
    conf = DatabaseConf()
    del conf.database_name
    try:
        print("Connecting to PostgreSQL server")
        connection = psycopg2.connect(
            user = conf.database_user,
            password = conf.database_password,
            host = conf.database_host,
            port = conf.database_port
        )

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        session = connection.cursor()
        try:
            session.execute("""CREATE USER airflow WITH PASSWORD 'airflow';""")
            connection.commit()
        except Exception as error:
            print("ERROR: [PRODUCT] - " + str(error))
            connection.rollback()
    except Exception as e:
        print(e)