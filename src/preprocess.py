import os
import pickle

import librosa
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import os
import subprocess as sp


class Loader:
    """Loader is responsible for loading an audio file."""

    def __init__(self, sample_rate, duration, mono):
        self.sample_rate = sample_rate
        self.duration = duration
        self.mono = mono

    def load(self, file_path):
        signal = librosa.load(file_path,
                              sr=self.sample_rate,
                              duration=self.duration,
                              mono=self.mono)[0]
        return signal


class Padder:
    """Padder is responsible to apply padding to an array."""

    def __init__(self, mode="constant"):
        self.mode = mode

    def left_pad(self, array, num_missing_items):
        padded_array = np.pad(array,
                              (num_missing_items, 0),
                              mode=self.mode)
        return padded_array

    def right_pad(self, array, num_missing_items):
        padded_array = np.pad(array,
                              (0, num_missing_items),
                              mode=self.mode)
        return padded_array


class LogSpectrogramExtractor:
    """LogSpectrogramExtractor extracts log spectrograms (in dB) from a
    time-series signal.
    """

    def __init__(self, frame_size, hop_length):
        self.frame_size = frame_size
        self.hop_length = hop_length

    def extract(self, signal):
        stft = librosa.stft(signal,
                            n_fft=self.frame_size,
                            hop_length=self.hop_length)[:-1]
        print(stft.shape)
        spectrogram = np.abs(stft)
        log_spectrogram = librosa.amplitude_to_db(spectrogram)
        return log_spectrogram


class MinMaxNormaliser:
    """MinMaxNormaliser applies min max normalisation to an array."""

    def __init__(self, min_val, max_val):
        self.min = min_val
        self.max = max_val

    def normalise(self, array):
        norm_array = (array - array.min()) / (array.max() - array.min() + 1e-6)
        norm_array = norm_array * (self.max - self.min) + self.min
        return norm_array

    def denormalise(self, norm_array, original_min, original_max):
        array = (norm_array - self.min) / (self.max - self.min)
        array = array * (original_max - original_min) + original_min
        return array


class Saver:
    """saver is responsible to save features, and the min max values."""

    def __init__(self, feature_save_dir, min_max_values_save_dir):
        self.feature_save_dir = feature_save_dir
        self.min_max_values_save_dir = min_max_values_save_dir

    def save_feature(self, feature, file_path):
        save_path = self._generate_save_path(file_path)
        np.save(save_path, feature)
        return save_path

    def save_min_max_values(self, min_max_values):
        save_path = os.path.join(self.min_max_values_save_dir,
                                 "min_max_values.pkl")
        self._save(min_max_values, save_path)

    @staticmethod
    def _save(data, save_path):
        with open(save_path, "wb") as f:
            pickle.dump(data, f)

    def _generate_save_path(self, file_path):
        file_name = os.path.split(file_path)[1]
        save_path = os.path.join(self.feature_save_dir, file_name + ".npy")
        return save_path


class PreprocessingPipeline:
    """PreprocessingPipeline processes audio files in a directory, applying
    the following steps to each file:
        1- load a file
        2- pad the signal (if necessary)
        3- extracting log spectrogram from signal
        4- normalise spectrogram
        5- save the normalised spectrogram

    Storing the min max values for all the log spectrograms.
    """

    def __init__(self):
        self.padder = None
        self.extractor = None
        self.normaliser = None
        self.saver = None
        self.min_max_values = {}
        self._loader = None
        self._num_expected_samples = None

    @property
    def loader(self):
        return self._loader

    @loader.setter
    def loader(self, loader):
        self._loader = loader
        self._num_expected_samples = int(loader.sample_rate * loader.duration)

    def process(self, audio_files_dir):
        for root, _, files in os.walk(audio_files_dir):
            file_paths = [os.path.join(root, file) for file in files]
            for file_path in file_paths:
                self._split_file_if_necessary(file_path, self.loader.duration)

        for root, _, files in os.walk(audio_files_dir):
            file_paths = [os.path.join(root, file) for file in files]
            for file_path in file_paths:
                self._process_file(file_path)
                print(f"Processed file {file_path}")
        self.saver.save_min_max_values(self.min_max_values)

    def _split_file_if_necessary(self, file_path, duration):
        try:
            # Command to get the total duration of the file in seconds
            duration_command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
            process = sp.Popen(duration_command, stdout=sp.PIPE, stderr=sp.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error occurred: stdout: {stdout.decode('utf-8')}", f"stderr: {stderr.decode('utf-8')}")
                return

            total_duration = float(stdout.strip())

            # Calculate the number of chunks
            num_chunks = int(total_duration // duration)

            # Split the file into chunks
            for i in range(num_chunks):
                start_time = i * duration
                ext = os.path.splitext(file_path)[1]
                output_file = f"{os.path.splitext(file_path)[0]}_{i}{ext}"
                
                # Command to split the file
                split_command = ['ffmpeg', '-i', file_path, '-ss', str(start_time), '-t', str(duration), '-vn', '-acodec', 'copy',  '-y', output_file]
                process = sp.Popen(split_command, stdout=sp.PIPE, stderr=sp.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    print(f"Error occurred: stdout: {stdout.decode('utf-8')}", f"stderr: {stderr.decode('utf-8')}")
                else:
                    print(f"Chunk {i} created")
                    
            os.remove(file_path)

            print(f"File {file_path} was split into {num_chunks} chunks of {duration} seconds each.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def _process_file(self, file_path):
        signal = self.loader.load(file_path)
        if self._is_padding_necessary(signal):
            signal = self._apply_padding(signal)
        feature = self.extractor.extract(signal)
        norm_feature = self.normaliser.normalise(feature)
        save_path = self.saver.save_feature(norm_feature, file_path)
        self._store_min_max_value(save_path, feature.min(), feature.max())

    
    def _is_padding_necessary(self, signal):
        if len(signal) < self._num_expected_samples:
            return True
        return False

    def _apply_padding(self, signal):
        num_missing_samples = self._num_expected_samples - len(signal)
        padded_signal = self.padder.right_pad(signal, num_missing_samples)
        return padded_signal

    def _store_min_max_value(self, save_path, min_val, max_val):
        self.min_max_values[save_path] = {
            "min": min_val,
            "max": max_val
        }

def preprocess():
    FRAME_SIZE = 512
    HOP_LENGTH = 256
    DURATION = 10.025 # in seconds
    SAMPLE_RATE = 22050
    MONO = True

    data_dir = os.getenv('DATA_DIR')
    SPECTROGRAMS_SAVE_DIR = os.path.join(data_dir, 'spectrograms')
    MIN_MAX_VALUES_SAVE_DIR = os.path.join(data_dir, 'fsdd')
    FILES_DIR = os.path.join(data_dir, 'input_files')

    os.makedirs(SPECTROGRAMS_SAVE_DIR, exist_ok=True)
    os.makedirs(MIN_MAX_VALUES_SAVE_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)

    # instantiate all objects
    loader = Loader(SAMPLE_RATE, DURATION, MONO)
    padder = Padder()
    log_spectrogram_extractor = LogSpectrogramExtractor(FRAME_SIZE, HOP_LENGTH)
    min_max_normaliser = MinMaxNormaliser(0, 1)
    saver = Saver(SPECTROGRAMS_SAVE_DIR, MIN_MAX_VALUES_SAVE_DIR)

    preprocessing_pipeline = PreprocessingPipeline()
    preprocessing_pipeline.loader = loader
    preprocessing_pipeline.padder = padder
    preprocessing_pipeline.extractor = log_spectrogram_extractor
    preprocessing_pipeline.normaliser = min_max_normaliser
    preprocessing_pipeline.saver = saver

    preprocessing_pipeline.process(FILES_DIR)

if __name__ == "__main__":
    preprocess()
