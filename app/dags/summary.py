try:
    from airflow import DAG
    from datetime import datetime, timedelta
    from airflow.operators.python_operator import PythonOperator
    from airflow.operators.python import task
    import psycopg2
    print("All modules are imported") # prints in log
except Exception as e:
    print(f"ERROR: {e}")


@task
def generate_aggrigation():
    aggrigation_query = """
                                INSERT INTO product_report 
                                SELECT name, count(*) FROM product
                                GROUP BY name;
                            """
    truncate_query = """
                                TRUNCATE product_report;
                            """
    # accessing connection
    try:
        connection = psycopg2.connect(user='postgres', password='postgres', host='localhost', port='5432', database='postman')
    except Exception as e:
        print(e)
    instance = connection


    print(instance)
    with instance.cursor() as cursor:
        try:
            cursor.execute(truncate_query)
            instance.commit()

            try:
                cursor.execute(aggrigation_query)
                instance.commit()
            except Exception as e:
                print(f"ERROR: {e}")
                instance.rollback()
        except Exception as e:
            print(f"ERROR: {e}")
            instance.rollback()
    
    print("SUCCESS: Aggrigation table created :)")

    try:
        connection.close()
        print("SUCCESS: Database connection closed")
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    return True

@task
def end_process(result):
    if result:
        print("Success") # logging
    else:
        print("Fail") #logging
    # try:
    #     connection.close()
    #     print("SUCCESS: Database connection closed")
    # except Exception as e:
    #     print(f"ERROR: {e}")



# arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2021, 3, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}


# dag instance 
with DAG(
        dag_id = "aggrigated_summary",
        schedule_interval='*/2 * * * *',
        default_args = default_args,
        catchup = False
    ) as dag:

    result = generate_aggrigation()
    end_process(result)
