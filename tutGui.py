from PyQt6 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import numpy as np
from scipy.fftpack import fft, fftfreq
from scipy.signal import get_window
import prototypUi
from rtlsdr import *
import time

class MainWindow(QtWidgets.QMainWindow, prototypUi.Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
 
        self.sdr = RtlSdr()
        self.conf_sdr()

        layout = QtWidgets.QVBoxLayout(self.graphDisplay)

        self.freqGraph = pg.PlotWidget()
        layout.addWidget(self.freqGraph)
        self.powerGraph = pg.PlotWidget()
        layout.addWidget(self.powerGraph)

        self.freqGraph.setTitle("Wykres Częstotliwościwy")
        self.freqGraph.setLabel('left', 'Amplituda')
        self.freqGraph.setLabel('bottom', 'Częstotliwości')
        
        self.powerGraph.setTitle("Wykres Mocy")
        self.powerGraph.setLabel('left', 'Moc(Db)')
        self.powerGraph.setLabel('bottom', 'Częstotliwość')

        pen = pg.mkPen(color='y', style=QtCore.Qt.PenStyle.DotLine)
        self.maxFreqDataLine = self.freqGraph.plot(pen=pen)
        pen = pg.mkPen(color=(255, 0, 0))
        self.freqDataLine =  self.freqGraph.plot(pen=pen)
        self.meanFreqDataLine =  self.freqGraph.plot(pen='g')
        self.proxyFreq = pg.SignalProxy(self.freqGraph.scene().sigMouseMoved, rateLimit=60, slot=self.freq_graph_mouse_moved)

        pen = pg.mkPen(color='y', style=QtCore.Qt.PenStyle.DotLine)
        self.maxPowerDataLine = self.powerGraph.plot(pen=pen)
        pen = pg.mkPen(color=(0, 0, 255))
        self.powerDataLine =  self.powerGraph.plot(pen=pen)
        self.meanPowerDataLine =  self.powerGraph.plot(pen='g')
        self.proxyPower = pg.SignalProxy(self.powerGraph.scene().sigMouseMoved, rateLimit=60, slot=self.power_graph_mouse_moved)

        self.startButton.clicked.connect(self.plot_real_time_signal)
        self.scanButton.clicked.connect(self.start_scan)
        self.displayButton.clicked.connect(self.display_signal)
        self.actionApplyYAxis.triggered.connect(self.applay_rangeY)
        self.windowedComboBox.currentTextChanged.connect(self.set_window)

        self.deviationEdit.setReadOnly(True)

        #Inicjalizacja tiemrów
        self.realTimer = QtCore.QTimer()
        self.scanTimer = QtCore.QTimer()
        self.displayTimer = QtCore.QTimer()
        self.realTimer.setInterval(50)
        self.scanTimer.setInterval(50)
        self.displayTimer.setInterval(50)
        
        self.isRealData = True
        self.isMeanDataVisible = False
        self.isMaxDataVisible = False
        self.scanFreqSpectrum = []
        self.scanMeanFreqSpectrum = []
        self.scanMaxFreqSpectrum = []
        self.scanPowerSpectrum = []
        self.scanMeanPowerSpectrum = []
        self.scanMaxPowerSpectrum = []
        self.scanFrequencies = []
        self.window = 'brak'

        #Do liczenia fps i czasu
        self.startTime = time.time()
        self.frameCount = 0
        self.fps = 0

    def set_window(self, win):
        match win:
            case 'Brak':
                self.window = 'brak'
                self.deviationEdit.setReadOnly(True)
            case 'Hamming':
                self.window = 'hamming'
                self.deviationEdit.setReadOnly(True)
            case 'Blackman':
                self.window = 'blackman'
                self.deviationEdit.setReadOnly(True)
            case 'Rectangular':
                self.window = 'boxcar'
                self.deviationEdit.setReadOnly(True)
            case 'Hanning':
                self.window = 'hann'
                self.deviationEdit.setReadOnly(True)
            case 'Gaussian':
                self.window = 'gaussian'
                self.deviationEdit.setReadOnly(False)
            case 'Triangular':
                self.window = 'triang'
                self.deviationEdit.setReadOnly(True)
        

    def get_window(self, signal):
        if(self.window == 'gaussian'):
            window = get_window((self.window, float(self.deviationEdit.text())), self.numberOfSamples)
            windowedSignal = signal * window
            return windowedSignal
        elif(self.window != 'brak'):
            window = get_window(self.window, self.numberOfSamples)
            windowedSignal = signal * window
            return windowedSignal
        else:
            return signal

    def applay_rangeY(self):
        viewRange = self.freqGraph.viewRange()
        currYRange = viewRange[1]
        self.freqGraph.setYRange(min=currYRange[0], max=currYRange[1], padding=0.1)

        viewRange = self.powerGraph.viewRange()
        currYRange = viewRange[1]
        self.powerGraph.setYRange(min=currYRange[0], max=currYRange[1], padding=0.1)

    #Blokowanie pól tekstowych i przycisków w aplikacji
    def block_edit(self):
        self.sampleRateEdit.setReadOnly(True)
        self.centralFrequencyEdit.setReadOnly(True)
        self.gainEdit.setReadOnly(True)
        self.scanTimeEdit.setReadOnly(True)
        self.numberOfSamplesEdit.setReadOnly(True)
        self.scanButton.setEnabled(False)
        self.displayButton.setEnabled(False)
        self.deviationEdit.setReadOnly(True)
        self.windowedComboBox.setEnabled(False)

    #Odblokowanie pól tekstowych i przycisków w aplikacji
    def unblock_edit(self):
        self.sampleRateEdit.setReadOnly(False)
        self.centralFrequencyEdit.setReadOnly(False)
        self.gainEdit.setReadOnly(False)
        self.scanTimeEdit.setReadOnly(False)
        self.numberOfSamplesEdit.setReadOnly(False)
        self.scanButton.setEnabled(True)
        self.displayButton.setEnabled(True)
        self.deviationEdit.setReadOnly(False)
        self.windowedComboBox.setEnabled(True)

    #Konfiguracja parametrów SDR-a
    def conf_sdr(self):
        self.sdr.sample_rate = float(self.sampleRateEdit.text())
        self.sampleRate = self.sdr.sample_rate
        self.sdr.center_freq = float(self.centralFrequencyEdit.text())
        self.centerFreq = self.sdr.center_freq
        if int(self.gainEdit.text()) > 10 or int(self.gainEdit.text()) < 0:
            self.sdr.gain = 10
            self.gainEdit.setText('10')
        else: 
            self.sdr.gain = int(self.gainEdit.text())
        self.gain = self.sdr.gain
        self.numberOfSamples = int(self.numberOfSamplesEdit.text())

    #Przygotowanie do wyświetlania danych w czasie rzeczywistym po kliknięciu przycisku 'Start'
    def plot_real_time_signal(self):
        if self.startButton.text() == "Start":
            self.startButton.setText("Stop")
            self.conf_sdr()
            self.block_edit()
            self.enableAVG.setEnabled(False)
            self.enableMax.setEnabled(False)
            self.meanFreqDataLine.clear()
            self.meanPowerDataLine.clear()
            self.maxFreqDataLine.clear()
            self.maxPowerDataLine.clear()
            self.realTimer.timeout.connect(self.update_plot_data)
            self.realTimer.start()
        else:
            #self.sdr.close()
            self.unblock_edit()
            self.startButton.setText("Start")
            self.realTimer.stop()
            self.enableAVG.setEnabled(True)
            self.enableMax.setEnabled(True)
            self.isMaxDataVisible = False
            self.isMeanDataVisible = False
            self.enableAVG.setChecked(False)
            self.enableMax.setChecked(False)

    def start_scan(self):
        print("Skanowanie rozpoczęte")
        self.isRealData = False
        self.block_edit()
        self.startButton.setEnabled(False)
        self.scanButton.setText("Skanowanie sygnału")
        self.currTime = time.time()
        self.conf_sdr()
        #Resetowanie zbiorów
        self.scanFreqSpectrum = []
        self.scanPowerSpectrum = []
        self.scanFrequencies = []
        self.scanTimer.timeout.connect(self.scan_signal)
        self.scanTimer.start()

        QtCore.QTimer.singleShot(int(self.scanTimeEdit.text()) * 1000, self.stop_scan)
        
    def scan_signal(self):
        print(len(self.scanFreqSpectrum))
        freqSpectrum, freqs, powerSpectrum = self.fft_transformation()
        self.scanFreqSpectrum.append(freqSpectrum)
        self.scanPowerSpectrum.append(powerSpectrum)
        self.scanFrequencies = freqs
    
    def stop_scan(self):
        self.isRealData = True
        self.scanTimer.stop()
        self.scanButton.setText('Skanuj sygnał')

        print(time.time() - self.currTime)
        self.unblock_edit()
        self.startButton.setEnabled(True)

        #Tworzenie zbiorów uśredniających wartości
        self.scanMeanFreqSpectrum = np.mean(self.scanFreqSpectrum, axis=0)
        self.scanMeanPowerSpectrum = np.mean(self.scanPowerSpectrum, axis=0)
        self.scanMaxFreqSpectrum = np.max(self.scanFreqSpectrum, axis=0)
        self.scanMaxPowerSpectrum = np.max(self.scanPowerSpectrum, axis=0)

        print("skanowanie zakończone")

    def display_signal(self):
        print("Wyświetlanie rozpoczęte")
        self.block_edit()
        self.startButton.setEnabled(False)
        self.currTime = time.time()
        self.dataSetIndex = 0
        self.displayTimer.timeout.connect(self.update_scan_plot)
        self.displayTimer.start()
        QtCore.QTimer.singleShot(int(self.scanTimeEdit.text()) * 1000, self.stop_display)

    
    def stop_display(self):
        self.displayTimer.stop()
        print(time.time() - self.currTime)
        self.unblock_edit()
        self.startButton.setEnabled(True)
        print("Wyświetlanie zakończone")

    #Aktualizowanie wykresów danymi z skanowego wcześniej sygnału
    def update_scan_plot(self):

        self.freqDataLine.setData(self.scanFrequencies/1e6, self.scanFreqSpectrum[self.dataSetIndex])
        self.powerDataLine.setData(self.scanFrequencies/1e6, self.scanPowerSpectrum[self.dataSetIndex])
        self.dataSetIndex = (self.dataSetIndex + 1) % len(self.scanFreqSpectrum)

        if(self.enableAVG.isChecked() == True):
            if not self.isMeanDataVisible:
                self.meanFreqDataLine.setData(self.scanFrequencies/1e6, self.scanMeanFreqSpectrum)
                self.meanPowerDataLine.setData(self.scanFrequencies/1e6, self.scanMeanPowerSpectrum)
                self.isMeanDataVisible = True
        else:
            if self.isMeanDataVisible:
                self.meanFreqDataLine.clear()
                self.meanPowerDataLine.clear()
                self.isMeanDataVisible = False
        
        if(self.enableMax.isChecked() == True):
            if not self.isMaxDataVisible:
                self.maxFreqDataLine.setData(self.scanFrequencies/1e6, self.scanMaxFreqSpectrum)
                self.maxPowerDataLine.setData(self.scanFrequencies/1e6, self.scanMaxPowerSpectrum)
                self.isMaxDataVisible = True
        else:
            if self.isMaxDataVisible:
                self.maxFreqDataLine.clear()
                self.maxPowerDataLine.clear()
                self.isMaxDataVisible = False

        #Tymczasowy licznik klatek
        currentTime = time.time()
        self.frameCount += 1
        if currentTime - self.startTime >= 1.0:
            self.fps = self.frameCount / (currentTime - self.startTime)
            self.setWindowTitle(f"FPS: {self.fps:.2f}")

            self.frameCount = 0
            self.startTime = currentTime

    #Poddawanie sygnału transformacie fouriera i przekształcanie danych do wykresu mocy
    def fft_transformation(self):
        signal = self.sdr.read_samples(self.numberOfSamples)
        if(self.isRealData == False):
            signal = self.get_window(signal)

        fftSample = fft(signal) / len(signal) #wykres częstotliwości ma w miare znormalizowane wartości ale psd zrobiło fikołka
        fftFrequency = fftfreq(len(fftSample), 1/self.sampleRate)
        powerSpectrum = self.create_power_spectrum(fft(signal))
        fftFrequency = fftFrequency + self.centerFreq

        # zadabanie o ciągłość wykresu i usunięcie zawijania się linii
        fftSample = np.append(fftSample, fftSample[0])
        fftFrequency = np.append(fftFrequency, fftFrequency[0])
        powerSpectrum = np.append(powerSpectrum, powerSpectrum[0])
        middle = len(fftFrequency)//2
        fftSample[middle] = np.nan
        fftFrequency[middle] = np.nan
        powerSpectrum[middle] = np.nan

        
        return np.abs(fftSample), np.abs(fftFrequency), np.abs(powerSpectrum)


    def create_power_spectrum(self, fftSamples):
        powerSpectrum = np.abs(fftSamples)**2
        powerSpectrumDb = 10 * np.log10(powerSpectrum + np.finfo(float).eps)
        return powerSpectrumDb

    #Wyświetlanie danych w czasie rzczywistym
    def update_plot_data(self):
        fftSamples, freqs, powerSamples = self.fft_transformation()
        
        self.freqDataLine.setData(freqs/1e6, fftSamples)  # Update the data.
        self.powerDataLine.setData(freqs/1e6, powerSamples)

        #Tymczasowy licznik klatek
        currentTime = time.time()
        self.frameCount += 1
        if currentTime - self.startTime >= 1.0:
            self.fps = self.frameCount / (currentTime - self.startTime)
            self.setWindowTitle(f"FPS: {self.fps:.2f}")

            self.frameCount = 0
            self.startTime = currentTime

    #Metoda śledząca kursor poruszający się po powierzchni wykresu częstotliości
    def freq_graph_mouse_moved(self, evt):
        pos = evt[0]
        if self.freqGraph.sceneBoundingRect().contains(pos):
            mousePoint = self.freqGraph.plotItem.vb.mapSceneToView(pos)
            self.XLabel.setText(f"Częstotliwość: {mousePoint.x():.2f}")
            self.YLabel.setText(f"Amplituda: {mousePoint.y():.4f}")

    #Metoda śledząca kursor poruszający się po powierzchni wykresu mocy
    def power_graph_mouse_moved(self, evt):
        pos = evt[0]
        if self.powerGraph.sceneBoundingRect().contains(pos):
            mousePoint = self.powerGraph.plotItem.vb.mapSceneToView(pos)
            self.XLabel.setText(f"Częstotliwość: {mousePoint.x():.2f}")
            self.YLabel.setText(f"Moc(Db): {mousePoint.y():.2f}")


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())