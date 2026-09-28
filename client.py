"""STFT Spectrogram & Mel-Filterbank Audio Feature Extraction Engine
100% Python Standard Library (math, cmath).
"""

import math
import cmath

class STFTMelFilterbankEngine:
    """Discrete Fourier Transform & Mel-Scaled Filterbank Energy Extractor."""
    def __init__(self, sample_rate=16000, n_fft=256, hop_length=128, n_mels=16):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        # Hann window
        self.window = [0.5 * (1.0 - math.cos(2.0 * math.pi * n / (n_fft - 1))) for n in range(n_fft)]

    def _dft(self, frame):
        N = len(frame)
        spectrum = []
        for k in range(N // 2 + 1):
            s = complex(0.0, 0.0)
            for n in range(N):
                angle = -2.0 * math.pi * k * n / N
                s += frame[n] * cmath.exp(complex(0, angle))
            spectrum.append(s)
        return spectrum

    def compute_stft(self, signal):
        frames = []
        num_frames = max(1, (len(signal) - self.n_fft) // self.hop_length + 1)
        for i in range(num_frames):
            start = i * self.hop_length
            chunk = signal[start : start + self.n_fft]
            if len(chunk) < self.n_fft:
                chunk = chunk + [0.0] * (self.n_fft - len(chunk))
            windowed = [chunk[j] * self.window[j] for j in range(self.n_fft)]
            spec = self._dft(windowed)
            mag = [abs(c) for c in spec]
            power = [m ** 2 for m in mag]
            frames.append(power)
        return frames

    def _hz_to_mel(self, hz):
        return 2595.0 * math.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel):
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def create_mel_filters(self):
        min_mel = self._hz_to_mel(0)
        max_mel = self._hz_to_mel(self.sample_rate / 2.0)
        mel_points = [min_mel + i * (max_mel - min_mel) / (self.n_mels + 1) for i in range(self.n_mels + 2)]
        hz_points = [self._mel_to_hz(m) for m in mel_points]
        bin_points = [int(math.floor((self.n_fft + 1) * hz / self.sample_rate)) for hz in hz_points]
        
        num_bins = self.n_fft // 2 + 1
        filter_bank = []
        for m in range(1, self.n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]
            f_filter = [0.0] * num_bins
            for k in range(f_m_minus, f_m):
                if f_m > f_m_minus and k < num_bins:
                    f_filter[k] = (k - bin_points[m - 1]) / (bin_points[m] - bin_points[m - 1])
            for k in range(f_m, f_m_plus):
                if f_m_plus > f_m and k < num_bins:
                    f_filter[k] = (bin_points[m + 1] - k) / (bin_points[m + 1] - bin_points[m])
            filter_bank.append(f_filter)
        return filter_bank

    def extract_log_mel_spectrogram(self, signal):
        power_stft = self.compute_stft(signal)
        mel_filters = self.create_mel_filters()
        log_mel_frames = []
        for frame_power in power_stft:
            mel_energies = []
            for mel_filter in mel_filters:
                energy = sum(p * w for p, w in zip(frame_power, mel_filter))
                log_energy = math.log(max(energy, 1e-10))
                mel_energies.append(log_energy)
            log_mel_frames.append(mel_energies)
        return {
            "num_frames": len(log_mel_frames),
            "n_mels": self.n_mels,
            "spectrogram": log_mel_frames
        }
