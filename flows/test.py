import sys
import os
from prefect import flow, task
from prefect.context import FlowRunContext
from dotenv import dotenv_values
from prefect.blocks.system import JSON
import json

@flow(log_prints=True)
def test():
    print('tessssssssssst')

if __name__ == "__main__":
    pass