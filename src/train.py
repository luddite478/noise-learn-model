print('asdasdasdasdasdasdasdasdasdaaaaaaaaaaaaaaa')
import os
import mlflow
import mlflow.keras
import secrets

import numpy as np

from autoencoder import VAE
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"

LEARNING_RATE = 0.0005
BATCH_SIZE    = 1
EPOCHS        = 25

data_dir             = os.getenv('DATA_DIR')
# MLFLOW_ARTIFACTS_DIR = os.getenv('MLFLOW_ARTIFACTS_DIR')
SPECTROGRAMS_PATH    = os.path.join(data_dir, 'spectrograms')
MODEL_DIR            = os.path.join(data_dir, 'model')

MLFLOW_URL          = os.getenv('MLFLOW_URL')
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

def train():
    with mlflow.start_run() as run:
        x_train = load_fsdd(SPECTROGRAMS_PATH)

        autoencoder = VAE(
            input_shape=(256, 864, 1),
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

        for epoch in range(EPOCHS):
            mlflow.log_metric("loss", history.history['loss'][epoch], step=epoch)
            mlflow.log_metric("_calculate_reconstruction_loss", history.history['_calculate_reconstruction_loss'][epoch], step=epoch)
            mlflow.log_metric("_calculate_kl_loss", history.history['_calculate_kl_loss'][epoch], step=epoch)

        autoencoder.save(MODEL_DIR)
        
        mlflow.log_artifact(MODEL_DIR)

    mlflow.end_run()

if __name__ == "__main__":
    train()


