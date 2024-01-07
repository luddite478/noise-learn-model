import sys
import os
# from prefect import flow, task
# from prefect.context import FlowRunContext
# from dotenv import dotenv_values
# from prefect.blocks.system import JSON
# import json

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)  
# print(sys.path)

from download import download as run_download
# from preprocess import preprocess as run_preprocess
# from train import train as run_training



from prefect import flow, task


@flow(log_prints=True)
def run_training_pipeline(items, params):
    items = [{'NAME': 'genocide organ - leichenlinie', 'LINK': 'https://youtu.be/4oqxZvUGXe4?si=6ql80J4T04ZYfORh'}]
    params = {
        'audio_length': 60
    }
    run_download(items, params)
    print('hello')