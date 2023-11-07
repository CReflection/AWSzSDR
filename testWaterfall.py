import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from scipy.signal import spectrogram

sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
center_freq = sdr.center_freq

sdr.gain = "auto"

NumberOfSamples = sample_rate*0.2

samples = sdr.read_samples(NumberOfSamples)

#diff_samples = fft(samples)

sdr.close()

frequencies, times, Sxx = spectrogram(samples, fs=sample_rate/1e6, window=np.hamming(2048), nperseg=2048, noverlap=1536)

shifted_frequencies = frequencies + center_freq

plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
plt.title('Spectrogram (Scipy)')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.colorbar(label='Intensity (dB)')
plt.tight_layout()
plt.show()