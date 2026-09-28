from client import STFTMelFilterbankEngine
import math

def main():
    engine = STFTMelFilterbankEngine(sample_rate=16000, n_fft=128, hop_length=64, n_mels=12)
    signal = [math.sin(2 * math.pi * 440 * i / 16000) for i in range(512)]
    res = engine.extract_log_mel_spectrogram(signal)
    print("STFT Spectrogram & Mel-Filterbank Verification:")
    print(f"Frames: {res['num_frames']}, Mel Filters: {res['n_mels']}")
    print(f"Sample Frame 0 Energies: {[round(x, 2) for x in res['spectrogram'][0][:5]]}")

if __name__ == "__main__":
    main()
