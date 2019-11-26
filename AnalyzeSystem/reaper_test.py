import pyreaper
from scipy.io import wavfile
import matplotlib.pyplot as plt

WAV_FILE = "..\AnalyzeSystem\datas\STONES_ana.wav"
fs, data = wavfile.read(WAV_FILE)

pm_times, pm, f0_times, f0, corr = pyreaper.reaper_internal(data[:,0].copy(order='C'), fs)
 
plt.plot(pm, linewidth=1, color="red", label="Pitch mark")
plt.show()
plt.plot( f0, linewidth=1, color="green", label="F0 contour")
plt.show()
plt.plot(corr, linewidth=1, color="blue", label="Correlations")
plt.show()