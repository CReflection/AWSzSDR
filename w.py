from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
from numpy import fft
import numpy as np

sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 168.525e6
center_freq = sdr.center_freq

sdr.gain = 'auto'  # Wartość wzmocnienia w dB, 'auto' może nie być poprawne
number_of_samples = int(sample_rate)
number_of_chunks = 3
samples = sdr.read_samples(number_of_samples*30)
sdr.close()

chunk_size = int(number_of_samples / number_of_chunks)
matrix = []

for count in range(number_of_chunks):
    chunk = samples[count*chunk_size:(count+1)*chunk_size]
    Fk = fft.fft(chunk) / len(chunk)
    nu = fft.fftfreq(len(chunk), 1/sample_rate)
    nu = (fft.fftshift(nu) + center_freq)/1e6  # Przesunięcie o częstotliwość środkową
    Fk = fft.fftshift(Fk)
    power = 10 * np.log10(np.abs(Fk)**2)
    matrix.append(power)

matrix = np.array(matrix)

plt.figure()
extent = [nu[0], nu[-1], 0, number_of_chunks]  # Zakresy dla osi X i Y
pc = plt.imshow(matrix, aspect='auto', extent=extent, cmap="viridis", origin='lower')
cbar = plt.colorbar(pc)
plt.ylabel('Chunk number')  # Powinno być czas, ale w tym kodzie mamy numer fragmentu
plt.xlabel('Frequency (MHz)')
plt.show()