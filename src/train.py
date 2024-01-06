import os

import numpy as np

from autoencoder import VAE
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"

LEARNING_RATE = 0.0005
BATCH_SIZE    = 1
EPOCHS        = 25

data_dir            = os.getenv('DATA_PATH')
SPECTROGRAMS_PATH   = os.path.join(data_dir, 'spectrograms')
MODEL_DIR           = os.path.join(data_dir, 'model')

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
    autoencoder.train(x_train, BATCH_SIZE, EPOCHS)
    autoencoder.save(MODEL_DIR)

if __name__ == "__main__":
    train()


