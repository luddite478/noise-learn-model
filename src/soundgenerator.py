import librosa

from preprocess import MinMaxNormaliser
import numpy as np

class SoundGenerator:
    """SoundGenerator is responsible for generating audios from
    spectrograms.
    """

    def __init__(self, vae, hop_length):
        self.vae = vae
        self.hop_length = hop_length
        self._min_max_normaliser = MinMaxNormaliser(0, 1)
        self.avg_min_max = {
            'min': -60,
            'max': 10
        }

    def generate(self, spectrograms, min_max_values):
        generated_spectrograms, latent_representations = \
            self.vae.reconstruct(spectrograms)
        signals = self.convert_spectrograms_to_audio(generated_spectrograms, min_max_values)
        return signals, latent_representations

    def convert_spectrograms_to_audio(self, spectrograms, min_max_values):
        signals = []
        for spectrogram, min_max_value in zip(spectrograms, min_max_values):
            # reshape the log spectrogram
            log_spectrogram = spectrogram[:, :, 0]
            # apply denormalisation
            denorm_log_spec = self._min_max_normaliser.denormalise(
                log_spectrogram, min_max_value["min"], min_max_value["max"])
            # log spectrogram -> spectrogram
            spec = librosa.db_to_amplitude(denorm_log_spec)
            # apply Griffin-Lim
            signal = librosa.istft(spec, hop_length=self.hop_length)
            # append signal to "signals"
            signals.append(signal)
        return signals

    def generate_unique(self, num_generated):
        signals = []
        for i in range(num_generated):
            random_seed = np.random.normal(0, 1, (1, 128))
            print('random_seed', random_seed.shape)
            sampled_spec = self.vae.decoder.predict(random_seed)
            log_spectrogram = np.squeeze(sampled_spec) 
            denorm_log_spec = self._min_max_normaliser.denormalise(
                    log_spectrogram, self.avg_min_max ["min"], self.avg_min_max ["max"])
            
            spec = librosa.db_to_amplitude(denorm_log_spec)
            signal = librosa.istft(spec, hop_length=self.hop_length)
            

            signals.append(signal)

        return signals
