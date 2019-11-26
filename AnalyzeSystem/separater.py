import numpy as np
from scipy.io import wavfile
import scipy.signal
from levinson_durbin import autocorr, LevinsonDurbin
import formant
import matplotlib.pyplot as plt
from scipy import interpolate

def check_formant(f):
	f1 = f[0]
	f2 = f[1] if len(f) > 2 else 0
	if 800 < f1 and f1 < 1400 and 900  < f2 and f2 < 2000: return 0.1 #あ
	if 100 < f1 and f1 < 500  and 1900 < f2 and f2 < 3500: return 0.2 #い
	if 100 < f1 and f1 < 700  and 1000 < f2 and f2 < 2000: return 0.3 #う
	if 400 < f1 and f1 < 800  and 1700 < f2 and f2 < 3000: return 0.4 #え
	if 300 < f1 and f1 < 900  and 500  < f2 and f2 < 1500: return 0.5 #お
	return -0.1

def calc_volume(data):
	v=0.0
	for x in data:
		v += abs(x)
	v = v / len(data)
	return v

WAV_FILE = "..\AnalyzeSystem\datas\STONES_ana.wav"
fs, data = wavfile.read(WAV_FILE)
calc_len = 0.02
vowel = []
formants = np.empty(((int)(len(data)/(calc_len*44100)),3))
data = data / 32768
temp_f2 = 0
for i in range((int)(len(data)/(calc_len*44100))):
	start_time = i*calc_len
	audio = data[(int)(start_time*44100):(int)(start_time*44100+calc_len*44100),0].astype(np.float)
	f = formant.calc_formant(audio, fs)
	if calc_volume(audio) > 0.05:
		vowel.extend([check_formant(f)] * (int)(calc_len * 44100))
		formants[i] = [f[0], f[1] if len(f) > 2 else temp_f2, f[2] if len(f) > 3 else 0]
		if f[1] != 0:
			temp_f2 = f[1]
	else:
		vowel.extend([0.0] * (int)(calc_len * 44100))
		formants[i] = [0,0,0]


plt.subplot(2,1,1)
plt.plot(data[:,0])
plt.plot(vowel, 'r')

plt.subplot(2, 1, 2)
plt.plot(range(0, len(formants)), formants)
plt.tight_layout()
plt.show()