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
print('MLFLOW_URL', MLFLOW_URL)
mlflow.set_tracking_uri(MLFLOW_URL)
mlflow.set_experiment("some")


def verify_mlflow_connection(experiment_name):
    if 'PREFECT_RUN_NAME' in os.environ:
        RUN_NAME = os.environ['PREFECT_RUN_NAME']
    else:
        RUN_NAME = secrets.token_hex(3)[:5]
    client = mlflow.tracking.MlflowClient()
    tracking_uri = mlflow.get_tracking_uri()
    print(f"Current tracking uri: {tracking_uri}")

    try:
        # Get experiment by name
        experiment = client.get_experiment_by_name(experiment_name)

        if experiment:
            # Get the last 5 runs of the experiment
            runs = client.search_runs(experiment.experiment_id, max_results=5)

            if len(runs) > 0:
                print("Connection to MLflow server was successful.")
                print(f"Here are the last 5 runs of the experiment {experiment_name}:")
                for run in runs:
                    print(f"Run ID: {run.info.run_id}, Start Time: {run.info.start_time}, End Time: {run.info.end_time}")
            else:
                print("Connection to MLflow server was successful, but there are no runs in the experiment.")
        else:
            print(f"No experiment with name {experiment_name} found.")

    except Exception as e:
        print(f"Failed to connect to MLflow server: {e}")

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

def mlflow_log_artifacts(source_dir):
    # ARTIFACTS_DIR = os.path.join(MLFLOW_ARTIFACTS_DIR, RUN_NAME)

    # if not os.path.exists(ARTIFACTS_DIR):
    #     os.makedirs(ARTIFACTS_DIR)

    mlflow.log_artifact(MODEL_DIR)

def train():
    with mlflow.start_run() as run:
        verify_mlflow_connection('some')
        print("Run ID:", run.info.run_id)
        print("Experiment ID:", run.info.experiment_id)

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
        print('RUN_NAME', RUN_NAME)
        mlflow.log_artifact(MODEL_DIR)

    mlflow.end_run()

if __name__ == "__main__":
    train()


