# app/models/product.py
import sys
sys.path.insert(1, '../')
import models
import psycopg2
import numpy as np

class Product(object):
    """
        Fields
            name : String
            sku : String [Primary Key, Not Null]
            description : String
            partition_code : custom partition code
    """

    def __init__(self):
        self.table_query =  """
                                CREATE TABLE product(
                                    name VARCHAR(100),
                                    sku VARCHAR(120) NOT NULL,
                                    description VARCHAR(500),
                                    partition_code INT NOT NULL,
                                    CONSTRAINT sku PRIMARY KEY(sku, partition_code)
                                ) PARTITION BY LIST(partition_code)
                            """
        self.session = models.ConnectDB().initialise()

        self. reporting_table_query = """
                                        CREATE TABLE product_report(
                                            name VARCHAR(100) NOT NULL,
                                            "no. of products" INT
                                        );
                                    """

        self.update_trigger = """
                                CREATE OR REPLACE FUNCTION update_product()
                                    RETURNS TRIGGER
                                    LANGUAGE PLPGSQL
                                AS
                                $$
                                    BEGIN
                                        DELETE FROM product where sku = NEW.sku AND partition_code = NEW.partition_code;
                                    END;
                                $$;
        
                            """

        self.scheduler_query = """
                                INSERT INTO product_report 
                                SELECT name, count(*) FROM product
                                GROUP BY name;
                            """


    def create_report_table(self):
        print(self.session)
        with self.session.cursor() as cursor:
            try:
                cursor.execute(self.reporting_table_query)
                self.session.commit()
            except Exception as error:
                print("ERROR: [PRODUCT] - " + str(error))
                self.session.rollback()


    def generate_report(self):
        try:
            with self.session.cursor() as cursor:
                cursor.execute(self.scheduler_query)
                self.session.commit()
        except Exception as e:
            self.session.rollback()



    def create_trigger(self):
        try:
            with self.session.cursor() as cursor:
                cursor.execute("""
                                CREATE TRIGGER update_record
                                BEFORE UPDATE ON product
                                FOR EACH STATEMENT
                                EXECUTE PROCEDURE update_product();
                            """)
        except Exception as e:
            print(e)


    def close_session(self):
        if self.session:
            self.session.close()
            print("INFO: [PRODUCT MODEL] - Connection Closed")

    def create_table(self):
        with self.session.cursor() as cursor:
            try:
                cursor.execute(self.table_query)
                self.session.commit()
            except Exception as error:
                print("ERROR: [PRODUCT] - " + str(error))
                self.session.rollback()

    def update_row(self, row):
        with self.session.cursor() as cursor:
            try:
                cursor.execute(f"""
                                UPDATE product
                                SET name = '{row[0]}',
                                    description = '{row[2]}'
                                WHERE sku = '{row[1]}' AND partition_code = {row[3]};
                            """)
                self.session.commit()
            except Exception as e:
                print(e)
                self.session.rollback()

    def drop_table(self):
        try:
            with self.session.cursor() as cursor:
                cursor.execute('DROP TABLE IF EXISTS product;')
                self.session.commit()
        except Exception as e:
            self.session.rollback()

    def create_partition(self, partition_count):
        # partition_count is not specified in the os environement
        # variable from utils.hashing module
        cursor = self.session.cursor()
        for count in range(partition_count):
            cursor.execute(f"""
                            CREATE TABLE product_{count} PARTITION OF product
                            FOR VALUES IN ({count});
            """)
            self.session.commit()

    def insert_one(self, row):
        with self.session.cursor() as cursor:
            try:
                cursor.execute(f"""
                                INSERT INTO product VALUES ('{row[0]}', '{row[1]}', '{row[2]}', {row[3]})
                """)
                self.session.commit()
            except (psycopg2.errors.UndefinedTable) as e:
                print("ERROR: [PRODUCT] - Table does not Exist")
                self.session.rollback()
            except (psycopg2.errors.UndefinedColumn,) as e :
                print("ERROR: [PRODUCT] - Undefined Column")
                self.session.rollback()
            except (psycopg2.errors.CheckViolation,) as e :
                print("ERROR: [PRODUCT] - Violation 'create partition'")
                self.session.rollback()
            except (psycopg2.errors.UniqueViolation,) as e:
                self.session.rollback()
                self.update_row(row)
                # print("ERROR: [PRODUCT] - Primay Key Already Exists - Record updated ")
                

        

