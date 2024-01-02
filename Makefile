include .local.env
DOCKER_SPECTROGRAMS_SAVE_DIR := $(shell grep ^SPECTROGRAMS_SAVE_DIR= .docker.env | cut -d '=' -f 2)
DOCKER_MIN_MAX_VALUES_SAVE_DIR := $(shell grep ^MIN_MAX_VALUES_SAVE_DIR= .docker.env | cut -d '=' -f 2)
DOCKER_FILES_DIR := $(shell grep ^FILES_DIR= .docker.env | cut -d '=' -f 2)
DOCKER_SRC_DIR := $(shell grep ^SRC_DIR= .docker.env | cut -d '=' -f 2)
DOCKER_SAVE_DIR_GENERATED := $(shell grep ^SAVE_DIR_GENERATED= .docker.env | cut -d '=' -f 2)

docker-build:
	docker build --progress=plain -t tf-2021-vae .

get-tensor:
	docker run -ti --gpus all --rm --env-file .docker.env -v $(PWD)/src:$(DOCKER_SRC_DIR) -v $(SPECTROGRAMS_SAVE_DIR):$(DOCKER_SPECTROGRAMS_SAVE_DIR) -v $(MIN_MAX_VALUES_SAVE_DIR):$(DOCKER_MIN_MAX_VALUES_SAVE_DIR) -v $(FILES_DIR):$(DOCKER_FILES_DIR) tf-2021-vae python get_tensor_size.py

preprocess:
	docker run -ti --gpus all --rm --env-file .docker.env -v $(PWD)/src:$(DOCKER_SRC_DIR) -v $(SPECTROGRAMS_SAVE_DIR):$(DOCKER_SPECTROGRAMS_SAVE_DIR) -v $(MIN_MAX_VALUES_SAVE_DIR):$(DOCKER_MIN_MAX_VALUES_SAVE_DIR) -v $(FILES_DIR):$(DOCKER_FILES_DIR) tf-2021-vae python preprocess.py

train:
	docker run -ti --gpus all --rm --env-file .docker.env -v $(PWD)/src:$(DOCKER_SRC_DIR) -v $(SPECTROGRAMS_SAVE_DIR):$(DOCKER_SPECTROGRAMS_SAVE_DIR) -v $(MIN_MAX_VALUES_SAVE_DIR):$(DOCKER_MIN_MAX_VALUES_SAVE_DIR) -v $(FILES_DIR):$(DOCKER_FILES_DIR) tf-2021-vae python train.py

generate:
	docker run -ti --gpus all --rm --env-file .docker.env -v $(PWD)/src:$(DOCKER_SRC_DIR) -v $(SPECTROGRAMS_SAVE_DIR):$(DOCKER_SPECTROGRAMS_SAVE_DIR) -v $(MIN_MAX_VALUES_SAVE_DIR):$(DOCKER_MIN_MAX_VALUES_SAVE_DIR) -v $(FILES_DIR):$(DOCKER_FILES_DIR) -v $(SAVE_DIR_GENERATED):$(DOCKER_SAVE_DIR_GENERATED) tf-2021-vae python generate.py


