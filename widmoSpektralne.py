from rtlsdr import RtlSdr
from scipy import signal
import matplotlib as plt
from pylab import *
import time
import threading
import numpy as np



sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
center_freq = sdr.center_freq

sdr.gain = 'auto'

samples = sdr.read_samples(sample_rate)
sdr.close()

plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')

show()
#f, t, Sxx = signal.spectrogram(samples, fs=sample_rate, window=np.hamming(2048), nperseg=2048, noverlap=1536, scaling="spectrum", mode="magnitude")
#pcolormesh(t, f, 20*np.log10(Sxx))

#show()
#print("siema")