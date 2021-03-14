from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
import sys


# declaring task
import psycopg2

def generate_report():
    scheduler_query = """
                                INSERT INTO product_report 
                                SELECT name, count(*) FROM product
                                GROUP BY name;
                            """
    try:
        with psycopg2.connect(user='postgres', password='postman', host='postgres', port='5432', database='postman') as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(scheduler_query)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
    except Exception as e:
        print(e)

def task_file():
    pass



# arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2021, 3, 13),
    'retries': 0,
}


# dag instance 
dag = DAG(dag_id='postman_1', default_args=default_args, catchup=False, schedule_interval='@once')

#  Task Instance
reporter = PythonOperator(
    task_id = 'report_products',
    python_callable = generate_report(),
    dag = dag,
)

end = PythonOperator(
    task_id = 'end_task',
    python_callable = task_file(),
    dag = dag,
)


reporter >> end
