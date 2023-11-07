from rtlsdr import RtlSdr
import matplotlib as plt
from pylab import *
import numpy as np
from numpy import fft



sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sample_rate = sdr.sample_rate
sdr.center_freq = 100e6
center_freq = sdr.center_freq

sdr.gain = 'auto'
numbe_of_samples = sample_rate*0.2
number_of_chunk = 3
samples = sdr.read_samples(sample_rate)
sdr.close()

chunk_size = round(numbe_of_samples/number_of_chunk)
matrix = np.zeros((chunk_size-2))
chunk = matrix

for count in range(1, number_of_chunk):
    chunk = samples[(count-1)*chunk_size:count*chunk_size-1]
    Fk = fft.fft(chunk)/np.size(chunk)
    nu = fft.fftfreq(np.size(chunk),2*0.5/sample_rate)
    Fk[0] = Fk[2]
    Fk = fft.fftshift(Fk)
    nu = fft.fftshift(nu)
    if count == 1:
        matrix = 10*np.log10(np.absolute(Fk)**2)
    else:
        matrix = np.vstack((matrix, 10*np.log10(np.absolute(Fk)**2)))

plt.figure()
pc = plt.pcolormesh(matrix, shading="gouraud", cmap="magma")
cbar = plt.colorbar(pc)
plt.show()