include .local.env

HOST_PROJECT_DIR = $(PWD)
HOST_DATA_DIR = $(PWD)/data
CONTAINER_PROJECT_DIR = /app
CONTAINER_DATA_DIR = /data
CONTAINER_SRC_DIR = /app/src
CONTAINER_FLOWS_DIR = /app/flows
DOCKER_IMAGE_NAME = $(DOCKERHUB_REGISTRY_SERVER)/$(DOCKERHUB_REGISTRY_REPO)
JUPYTER_TOKEN = abc

init:
	rm -rf $(HOST_DATA_DIR) && mkdir -p $(HOST_DATA_DIR)/input_files
	if [ ! -f .local.env ]; then cp example.local.env .local.env; fi

docker-build:
	docker build --progress=plain -t $(DOCKER_IMAGE_NAME) .

docker-build-dev:
	docker build --build-arg BASE_IMAGE=$(DOCKER_IMAGE_NAME) --progress=plain -t $(DOCKER_IMAGE_NAME):dev -f ./Dockerfile.dev .

jupyter-docker:
	docker run -ti --gpus all --rm \
		--name jupyter \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		-p 8888:8888 \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME):dev jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.allow_origin='*' --NotebookApp.token=$(JUPYTER_TOKEN)

docker-exec:
	docker run -ti --gpus all --rm \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME):dev bash

docker-push:
	echo "$(DOCKERHUB_REGISTRY_PASSWORD)" | \
	docker login -u $(DOCKERHUB_REGISTRY_USER) --password-stdin $(DOCKERHUB_REGISTRY_SERVER)
	docker push $(DOCKER_IMAGE_NAME)

prefect-deploy:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_PROJECT_DIR) \
		$(DOCKER_IMAGE_NAME) /bin/bash -c "prefect cloud login --key $(PREFECT_API_KEY) && prefect deploy --all"

get-tensor:
	docker run -ti --gpus all --rm \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) python get_tensor_size.py

download:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) python download.py

preprocess:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) python preprocess.py

train:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		-e MLFLOW_ARTIFACT_STORE=$(CONTAINER_DATA_DIR)  \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) python train.py

generate:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w  $(CONTAINER_SRC_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) python generate.py

run-training-pipeline-local:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_FLOWS_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) /bin/bash -c "prefect cloud login --key $(PREFECT_API_KEY) && python run_training_pipeline.py"

run-training-pipeline-infra:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_FLOWS_DIR) \
		-e DATA_DIR=$(CONTAINER_DATA_DIR) \
		--env-file .local.env \
		$(DOCKER_IMAGE_NAME) /bin/bash -c "prefect cloud login --key $(PREFECT_API_KEY) && prefect deployment run run-training-pipeline/training"