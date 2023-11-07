from rtlsdr import *
import matplotlib.pyplot as plt
import numpy as np

sdr = RtlSdr()
sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
center_freq = sdr.center_freq
sdr.gain = 0
NumberOfSamples = 2500  # Możesz dostosować tę wartość do swoich potrzeb

# Odczytaj próbki z urządzenia RTL-SDR
signal = sdr.read_samples(NumberOfSamples)

fft_result = np.fft.fft(signal)
fft_freq = np.fft.fftfreq(len(fft_result), 1/NumberOfSamples)  # Wektor częstotliwości

fft_freq = (fft_freq * sample_rate / len(fft_result)) + center_freq
# Wykreśl wyniki
plt.figure(figsize=(10, 4))
plt.plot(fft_freq / 1e6, 10 * np.log10(np.abs(fft_result)) / len(fft_result))  # Skala logarytmiczna dla mocy
plt.title('Analiza widma częstotliwości')
plt.xlabel('Częstotliwość (MHz)')
plt.ylabel('Moc (dB)')
plt.grid()
plt.show()