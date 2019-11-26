import numpy as np
from scipy.io import wavfile
import scipy.signal
from levinson_durbin import autocorr, LevinsonDurbin
import formant
import matplotlib.pyplot as plt
from scipy import interpolate
import pyreaper
import pandas as pd

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

def EWMA_Outlier_Check(target):  # 指数加重移動平均外れ値修正
	target = pd.Series(target)
	ewm_mean = target.ewm(span=90).mean()
	ewm_std = target.ewm(span=90).std()
	return np.array(list(map(lambda t, mean, std: t if abs(mean - t) < std * 2 else mean, target, ewm_mean, ewm_std)))

def EWMA_Filter(target):
	target = pd.Series(target)
	ewm_mean = target.ewm(span=90).mean()
	return np.array(list(map(lambda t, mean: mean, target, ewm_mean)))

def read_lab_file(path):
	f = open(path)
	l = f.read().split("\n")
	time_and_soundele = []
	for i in l:
		tas = i.split(" ")
		if len(tas) == 3:
			time_and_soundele.append([float(tas[0]), float(tas[1]), tas[2]])
	return time_and_soundele

def lab_to_graph(lab_list):
	graph_array = []
	lab_vowel = []
	for i in range(len(lab_list)):
		print(lab_list[i][2] == "silE")
		if lab_list[i][2] is "a" or lab_list[i][2] is "i" or lab_list[i][2] is "u" or lab_list[i][2] is "e" or lab_list[i][2] is "o":
			element = 0
			if lab_list[i][2] is "a":
				element = 5
			elif lab_list[i][2] is "i":
				element = 4
			elif lab_list[i][2] is "u":
				element = 3
			elif lab_list[i][2] is "e":
				element = 2
			elif lab_list[i][2] is "o":
				element = 1
			lab_vowel.append([lab_list[i-1][0],element])
			lab_vowel.append([lab_list[i][1], element])
		elif lab_list[i][2] is "silB" or lab_list[i][2] is "silE":
			print("sil")
			lab_vowel.append([lab_list[i][0],0])
			lab_vowel.append([lab_list[i][1], 0])
	
	print(lab_vowel)
	import sys
	sys.exit(0)

	for e in lab_list:
		if e[2] is "a" or e[2] is "i" or e[2] is "u" or e[2] is "e" or e[2] is "o":
			element = 0
			if e[2] is "a":
				element = 5
			elif e[2] is "i":
				element = 4
			elif e[2] is "u":
				element = 3
			elif e[2] is "e":
				element = 2
			elif e[2] is "o":
				element = 1
			graph_array.append([e[1], element])
		elif e[2] is "silB" or e[2] is "silE":
			graph_array.append([e[0],0])
			graph_array.append([e[1],0])
		else:
			graph_array.append([e[0]])
	return graph_array



WAV_FILE = r"..\AnalyzeSystem\datas\STONES_ana.wav"
LAB_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\segmentation-kit\wav\STONES.lab"

Sound_Element =  read_lab_file(LAB_FILE)
lab_to_graph(Sound_Element)

fs, data = wavfile.read(WAV_FILE)
pm_times, pm, f0_times, f0, corr = pyreaper.reaper_internal(data[:, 0].copy(order='C'), fs)
calc_len = 0.005
vowel = []
f_mark =np.empty((int)(len(data)/(calc_len*44100)))
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
		f_mark[i]=1
	else:
		vowel.extend([0.0] * (int)(calc_len * 44100))
		formants[i] = [0, 0, 0]
		f_mark[i]=0

f0_diff = np.diff(f0)
f1_diff = np.diff(formants[:, 0])
f2_diff = np.diff(formants[:, 1])
#外れ値除外処理

f0_EWMA = EWMA_Outlier_Check(f0)
f1_EWMA = EWMA_Outlier_Check(formants[:,0])
f2_EWMA = EWMA_Outlier_Check(formants[:,1])

f_times = np.arange(0.0, len(data) / 44100, calc_len)

plt.subplot(3,1,1)
plt.plot(f_times,f_mark*100)
plt.plot(f0_times, f0_EWMA)

plt.subplot(3, 1, 2)
plt.plot(f_times,f_mark*100)
plt.plot(f_times, f1_EWMA)
# plt.plot(f0_times, f0)
# plt.plot(f_times,formants[:,:2])

plt.subplot(3, 1, 3)
plt.plot(f_times,f_mark*100)
plt.plot(f_times, f2_EWMA)

plt.tight_layout()
plt.show()