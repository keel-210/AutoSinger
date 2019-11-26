import numpy as np
from scipy.io import wavfile
import scipy.signal
from levinson_durbin import autocorr, LevinsonDurbin
import formant
import matplotlib.pyplot as plt

def check_formant(f):
	f1 = f[0]
	f2 = f[1]
	if f1 > 600 and f1 < 1400 and 900  < f2 and f2 < 2000: return 0.1 #あ
	if f1 > 100 and f1 < 410  and 1900 < f2 and f2 < 3500: return 0.2 #い
	if f1 > 100 and f1 < 700  and 1100 < f2 and f2 < 2000: return 0.3 #う
	if f1 > 400 and f1 < 800  and 1700 < f2 and f2 < 3000: return 0.4 #え
	if f1 > 300 and f1 < 900  and 500  < f2 and f2 < 1300: return 0.5 #お
	return 0

def calc_volume(data):
	v=0.0
	for x in data:
		v += abs(x)
	v = v / len(data)
	return v

WAV_FILE = "..\AnalyzeSystem\datas\STONES_ana.wav"
fs, data = wavfile.read(WAV_FILE)
calc_len = 0.04
formants = []
data=data/32768
for i in range((int)(len(data)/(calc_len*44100))):
	start_time = i*calc_len
	audio = data[(int)(start_time*44100):(int)(start_time*44100+calc_len*44100),0].astype(np.float)
	f = formant.calc_formant(audio, fs)
	# formants.extend([calc_volume(audio)]*(int)(calc_len*44100))
	if calc_volume(audio) > 0.1:
		formants.extend([check_formant(f)]*(int)(calc_len*44100))
	else:
		formants.extend([0.0]*(int)(calc_len*44100))

plt.plot(data[:,0])
plt.plot(formants,'r')
plt.show()