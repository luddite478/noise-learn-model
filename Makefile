include .local.env
HOST_DATA_DIR = $(PWD)/data
HOST_PROJECT_DIR = $(PWD)
CONTAINER_PROJECT_DIR = /app
CONTAINER_DATA_DIR = /data
CONTAINER_SRC_DIR = /app/src
CONTAINER_FLOWS_DIR = /app/flows

init:
	rm -rf $(HOST_DATA_DIR) && mkdir -p $(HOST_DATA_DIR)/input_files

docker-build:
	docker build --progress=plain -t tf-2021-vae .

get-tensor:
	docker run -ti --gpus all --rm \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		tf-2021-vae python get_tensor_size.py

download:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		tf-2021-vae python download.py

preprocess:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		tf-2021-vae python preprocess.py

train:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_SRC_DIR) \
		tf-2021-vae python train.py

generate:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w  $(CONTAINER_SRC_DIR) \
		tf-2021-vae python generate.py

run-training-pipeline:
	docker run -ti --gpus all --rm \
		-v $(HOST_DATA_DIR):$(CONTAINER_DATA_DIR) \
		-v $(HOST_PROJECT_DIR):$(CONTAINER_PROJECT_DIR) \
		-w $(CONTAINER_FLOWS_DIR) \
		tf-2021-vae /bin/bash -c "prefect cloud login --key $(PREFECT_API_KEY) && python run_training_pipeline.py"


