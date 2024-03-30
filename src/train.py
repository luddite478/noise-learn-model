import os
import mlflow
import mlflow.keras
import secrets

import numpy as np

from autoencoder import VAE
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"

LEARNING_RATE = 0.0001
BATCH_SIZE    = 32
EPOCHS        = 3000

data_dir             = os.getenv('DATA_DIR')
SPECTROGRAMS_PATH    = os.path.join(data_dir, 'spectrograms')
MODEL_DIR            = os.path.join(data_dir, 'model')


os.environ["AWS_ACCESS_KEY_ID"]      = os.getenv('S3_ACCESS_KEY')
os.environ["AWS_SECRET_ACCESS_KEY"]  = os.getenv('S3_SECRET_KEY')
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv('S3_URL')
MLFLOW_URL                           = os.getenv('MLFLOW_URL')
mlflow.set_tracking_uri(MLFLOW_URL)

def load_fsdd(spectrograms_path):
    x_train = []
    for root, _, file_names in os.walk(spectrograms_path):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            spectrogram = np.load(file_path) # (n_bins, n_frames, 1)
            x_train.append(spectrogram)
    x_train = np.array(x_train)
    x_train = x_train[..., np.newaxis] # -> (3000, 256, 64, 1)
    return x_train

def log_metrics(history, EPOCHS):
    percent = 1  # Change this to log every n percent
    log_interval = EPOCHS * percent // 100  # Calculate the number of epochs that represent each percent

    for epoch in range(EPOCHS):
        if epoch % log_interval == 0 or epoch == EPOCHS - 1:  # Also log for the last epoch
            print(f'Uploading epoch {epoch} metrics...')
            mlflow.log_metric("loss", history.history['loss'][epoch], step=epoch)
            mlflow.log_metric("_calculate_reconstruction_loss", history.history['_calculate_reconstruction_loss'][epoch], step=epoch)
            mlflow.log_metric("_calculate_kl_loss", history.history['_calculate_kl_loss'][epoch], step=epoch)

def train():
    with mlflow.start_run() as run:
        x_train = load_fsdd(SPECTROGRAMS_PATH)

        # autoencoder = VAE(
        #     input_shape=(256, 864, 1),
        #     conv_filters=(512, 256, 128, 64, 32),
        #     conv_kernels=(3, 3, 3, 3, 3),
        #     conv_strides=(2, 2, 2, 2, (2, 1)),
        #     latent_space_dim=128
        # )

        autoencoder = VAE(
            input_shape=(256, 64, 1),
            conv_filters=(512, 256, 128, 64, 32),
            conv_kernels=(3, 3, 3, 3, 3),
            conv_strides=(2, 2, 2, 2, (2, 1)),
            latent_space_dim=128
        )

        autoencoder.summary()
        autoencoder.compile(LEARNING_RATE)

        mlflow.log_param("learning_rate", LEARNING_RATE)
        mlflow.log_param("batch_size", BATCH_SIZE)
        mlflow.log_param("epochs", EPOCHS)

        history = autoencoder.train(x_train, BATCH_SIZE, EPOCHS)
        log_metrics(history, EPOCHS)
        autoencoder.save(MODEL_DIR)

        # mlflow.log_artifact(MODEL_DIR)
        # mlflow.log_artifact(GENERATED_DIR)
        # mlflow.log_artifact(ORIGINAL_DIR)
        #TODO mlflow.log_model

    mlflow.end_run()

if __name__ == "__main__":
    train()


