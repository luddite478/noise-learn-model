import os
import pickle

import numpy as np
import soundfile as sf

from soundgenerator import SoundGenerator
from autoencoder import VAE

from dotenv import load_dotenv
load_dotenv()

HOP_LENGTH = 256
data_dir = os.getenv('DATA_DIR')
SPECTROGRAMS_PATH   = os.path.join(data_dir, 'spectrograms')
MIN_MAX_VALUES_PATH = os.path.join(data_dir, 'fsdd/min_max_values.pkl') 
SAVE_DIR_ORIGINAL = os.path.join(data_dir, 'original')
SAVE_DIR_GENERATED = os.path.join(data_dir, 'generated')
MODEL_DIR           = os.path.join(data_dir, 'model')

os.makedirs(SAVE_DIR_ORIGINAL, exist_ok=True)
os.makedirs(SAVE_DIR_GENERATED, exist_ok=True)

def load_fsdd(spectrograms_path):
    x_train = []
    file_paths = []
    for root, _, file_names in os.walk(spectrograms_path):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            spectrogram = np.load(file_path) # (n_bins, n_frames, 1)
            x_train.append(spectrogram)
            file_paths.append(file_path)
    x_train = np.array(x_train)
    x_train = x_train[..., np.newaxis] # -> (3000, 256, 64, 1)
    return x_train, file_paths


def select_spectrograms(spectrograms,
                        file_paths,
                        min_max_values,
                        num_spectrograms=2):
    sampled_indexes = np.random.choice(range(len(spectrograms)), num_spectrograms)
    sampled_spectrogrmas = spectrograms[sampled_indexes]
    for p in file_paths:
        print(p)
    file_paths = [file_paths[index] for index in sampled_indexes]
    sampled_min_max_values = [min_max_values[file_path] for file_path in
                           file_paths]
    return sampled_spectrogrmas, sampled_min_max_values


def save_signals(signals, save_dir, sample_rate=22050):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for i, signal in enumerate(signals):
        save_path = os.path.join(save_dir, str(i) + ".wav")
        sf.write(save_path, signal, sample_rate)


def test_generate():
    # initialise sound generator
    vae = VAE.load(MODEL_DIR)
    sound_generator = SoundGenerator(vae, HOP_LENGTH)

    # load spectrograms + min max values
    with open(MIN_MAX_VALUES_PATH, "rb") as f:
        min_max_values = pickle.load(f)

    specs, file_paths = load_fsdd(SPECTROGRAMS_PATH)

    # sample spectrograms + min max values
    sampled_specs, sampled_min_max_values = select_spectrograms(specs,
                                                                file_paths,
                                                                min_max_values,
                                                                5)

    # generate audio for sampled spectrograms
    signals, _ = sound_generator.generate(sampled_specs,
                                          sampled_min_max_values)

    # convert spectrogram samples to audio
    original_signals = sound_generator.convert_spectrograms_to_audio(
        sampled_specs, sampled_min_max_values)

    # save audio signals
    save_signals(signals, SAVE_DIR_GENERATED)
    save_signals(original_signals, SAVE_DIR_ORIGINAL)

def compare_signals(signals):
    for i, signal in enumerate(signals):
        print(f'Signal {i+1}: Mean={np.mean(signal)}, StdDev={np.std(signal)}')

def generate_unique():
    vae = VAE.load(MODEL_DIR)
    sound_generator = SoundGenerator(vae, HOP_LENGTH)
    signals = sound_generator.generate_unique(5)
    compare_signals(signals)
    save_signals(signals, SAVE_DIR_GENERATED)



if __name__ == "__main__":
    # test_generate()
    generate_unique()
    # # initialise sound generator
    # vae = VAE.load("model")
    # sound_generator = SoundGenerator(vae, HOP_LENGTH)

    # random_seed = np.random.normal(0, 1, (1, vae.latent_dim))
    # sampled_spec = vae.decoder.predict(random_seed)
    # signal = sound_generator.generate_from_random_seed(random_seed)


    # # save audio signals
    # save_signals(signals, SAVE_DIR_GENERATED)
    # vae = VAE.load("model")
    # sound_generator = SoundGenerator(vae, HOP_LENGTH)

    # # load spectrograms + min max values
    # # with open(MIN_MAX_VALUES_PATH, "rb") as f:
    # #     min_max_values = pickle.load(f)

    # # specs, file_paths = load_fsdd(SPECTROGRAMS_PATH)

    # # # sample spectrograms + min max values
    # # sampled_specs, sampled_min_max_values = select_spectrograms(specs,
    # #                                                             file_paths,
    # #                                                             min_max_values,
    # #                                                             5)
    # # print('sampled_specs', sampled_specs.shape)
    # # generate audio for sampled spectrograms
    # signals = sound_generator.generate_from_random_seed(1)
    # # signals, _ = sound_generator.generate(sampled_specs,
    # #                                       sampled_min_max_values)

    # # # # convert spectrogram samples to audio
    # # # original_signals = sound_generator.convert_spectrograms_to_audio(
    # # #     sampled_specs, sampled_min_max_values)

    # # # save audio signals
    # save_signals(signals, SAVE_DIR_GENERATED)
    # save_signals(original_signals, SAVE_DIR_ORIGINAL)
