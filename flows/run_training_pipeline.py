import sys
import os
from prefect import flow, task
from prefect.context import FlowRunContext
from dotenv import dotenv_values
from prefect.blocks.system import JSON
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)  

from download import download as run_download
from preprocess import preprocess as run_preprocess
from train import train as run_training

env_json = JSON.load("noise-gen-model-env")
env = env_json.value
for key, value in env.items():
    os.environ[key] = value

@task
def download(items, params):
    print("Downloading...")
    run_download(items, params)

@task
def preprocess():
    print("Preprocessing...")
    run_preprocess()
    
@task
def train():
    print("training")
    run_training()

# @task
# def upload():
#     print("uploading")


@flow(log_prints=True)
def run_training_pipeline(items, params):
    params['run_name'] = FlowRunContext.get().flow_run.dict().get('name')
    download(items, params)
    # files = download(items, params)
    preprocess()
    train()
    # upload()

if __name__ == "__main__":
    items = [{'NAME': 'genocide organ - leichenlinie', 'LINK': 'https://youtu.be/4oqxZvUGXe4?si=6ql80J4T04ZYfORh'}]
    params = {
        'audio_length': 60
    }
    run_training_pipeline(items, params)