import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

# Przykładowe dane
t = np.linspace(0, 10, 2000)
x = np.sin(t) + np.sin(3*t) + np.random.randn(t.shape[0]) * 0.5

frequencies, times, Sxx = spectrogram(x, fs=200, nperseg=256, noverlap=128)

plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
plt.title('Spectrogram (Scipy)')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.colorbar(label='Intensity (dB)')
plt.tight_layout()
plt.show()