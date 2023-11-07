from rtlsdr import RtlSdr
import matplotlib.pyplot as plt

# Inicjalizacja urządzenia RTL-SDR
sdr = RtlSdr()

# Ustaw parametry urządzenia
sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
sdr.gain = 'auto'

# Określ liczbę próbek, które chcesz odczytać
NumberOfSamples = 100  # Możesz dostosować tę wartość do swoich potrzeb

# Odczytaj próbki z urządzenia RTL-SDR
samples = sdr.read_samples(NumberOfSamples)

# Zamknij urządzenie RTL-SDR
sdr.close()

# Utwórz wykres dziedziny czasu
plt.figure(figsize=(10, 4))
plt.plot(samples)
plt.title('Sygnał w dziedzinie czasu')
plt.xlabel('Próbki')
plt.ylabel('Amplituda')
plt.grid()
plt.show()