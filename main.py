from rtlsdr import *
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np

sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
center_freq = sdr.center_freq

sdr.gain = "auto"

NumberOfSamples = sample_rate

samples = sdr.read_samples(NumberOfSamples)

#diff_samples = fft(samples)

sdr.close()

print(samples)
#print(diff_samples)

#max_freq_index = np.argmax(np.abs(diff_samples))
#dominant_freq = max_freq_index * sample_rate / NumberOfSamples
#print("Dominant Frequency: {} Hz".format(dominant_freq))

plt.psd(samples, Fs=sample_rate/1e6, Fc=center_freq/1e6)
plt.title('Widmo sygnału przy x próbkach')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')

del samples
plt.show()

#plt.figure(figsize=(8, 6))
#plt.plot(np.abs(diff_samples))
#plt.title('Amplitude Spectrum')
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('Amplitude')
#plt.grid()
#plt.show()
