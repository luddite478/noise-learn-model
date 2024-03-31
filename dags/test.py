from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 31),
    'retries': 1
}

# Instantiate the DAG object
dag = DAG(
    'multiple_steps_dag',
    default_args=default_args,
    description='A simple DAG with multiple steps',
    schedule_interval="@hourly"
)

# Define three tasks

def task1_function():
    print("Executing Task 1")

task1 = PythonOperator(
    task_id='task1',
    python_callable=task1_function,
    dag=dag
)

def task2_function():
    print("Executing Task 2")

task2 = PythonOperator(
    task_id='task2',
    python_callable=task2_function,
    dag=dag
)

def task3_function():
    print("Executing Task 3")

task3 = PythonOperator(
    task_id='task3',
    python_callable=task3_function,
    dag=dag
)

# Define task dependencies
task1 >> task2 >> task3
