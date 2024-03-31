from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
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

task1 = KubernetesPodOperator(
    task_id='task1',
    namespace='default',  # Update with your namespace
    image='python:latest',  # Use the latest Python image from Docker Hub
    cmds=['python', '-c', 'print("Executing Task 1")'],
    dag=dag
)

def task2_function():
    print("Executing Task 2")

task2 = KubernetesPodOperator(
    task_id='task2',
    namespace='default',  # Update with your namespace
    image='python:latest',  # Use the latest Python image from Docker Hub
    cmds=['python', '-c', 'print("Executing Task 2")'],
    dag=dag
)

def task3_function():
    print("Executing Task 3")

task3 = KubernetesPodOperator(
    task_id='task3',
    namespace='default',  # Update with your namespace
    image='python:latest',  # Use the latest Python image from Docker Hub
    cmds=['python', '-c', 'print("Executing Task 3")'],
    dag=dag
)
