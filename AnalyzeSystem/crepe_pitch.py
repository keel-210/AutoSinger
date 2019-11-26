from scipy.io import wavfile
import crepe
import matplotlib.pyplot as plt

WAV_FILE = "..\AnalyzeSystem\datas\STONES_ana.wav"

fs, data = wavfile.read(WAV_FILE)
time, frequency, confidence, activation = crepe.predict(data, fs, viterbi=True)

plt.plot(frequency)
plt.show()