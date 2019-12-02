import numpy as np
from scipy.io import wavfile
import scipy.signal
from levinson_durbin import autocorr, LevinsonDurbin
import formant
import matplotlib.pyplot as plt
from scipy import interpolate
import pyreaper
import pandas as pd

def EWMA_Outlier_Check(target,ewm_span):  # 指数加重移動平均外れ値修正
	target = pd.Series(target)
	ewm_mean = target.ewm(span=ewm_span).mean()
	ewm_std = target.ewm(span=ewm_span).std()
	return np.array(list(map(lambda t, mean, std: t if abs(mean - t) < std * 2 else mean, target, ewm_mean, ewm_std)))

def EWMA_Filter(target,ewm_span):
	target = pd.Series(target)
	ewm_mean = target.ewm(span=ewm_span).mean()
	return np.array(list(map(lambda mean: mean, ewm_mean)))

def calc_volume(data):
	v=0.0
	for x in data:
		v += abs(x)
	v = v / len(data)
	return v

def read_lab_file(path): #labファイルを配列に
	f = open(path)
	l = f.read().split("\n")
	time_and_soundele = []
	for i in l:
		tas = i.split(" ")
		if len(tas) == 3:
			time_and_soundele.append([float(tas[0]), float(tas[1]), tas[2]])
	return time_and_soundele

def lab_to_graph(lab_list):#labファイルから母音音素を数値化
	lab_vowel = []
	for i in range(len(lab_list)):
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
			if lab_list[i - 1][2] is "a" or lab_list[i - 1][2] is "i" or lab_list[i - 1][2] is "u" or lab_list[i - 1][2] is "e" or lab_list[i - 1][2] is "o":
				lab_vowel.append([lab_list[i][0],element])
			else:
				lab_vowel.append([lab_list[i-1][0],element])
			lab_vowel.append([lab_list[i][1], element])
		elif lab_list[i][2] == "silB" or lab_list[i][2] == "silE":
			lab_vowel.append([lab_list[i][0],0])
			lab_vowel.append([lab_list[i][1], 0])
	return np.array(lab_vowel)
def make_se_list():  #vsq4用の音素リストを作成する
	

def needle_remover(l,needle_size): #突出値除外
	for i in range(len(l) - (needle_size + 2) + 1):
		if l[i] == l[i + needle_size + 1]:
			l[i + 1:i + needle_size+1] = [(l[i] + l[i + needle_size + 1]) / 2]*needle_size
	return l

def f0_change_check(diff):
	#ざっくり書いてみる
	change_list = [0 if d >= -5 else 1 for d in diff]
	needle_remover(change_list,1)
	return np.array(change_list)

def SoundElement_process(diff, mark):
	DeplicateFlag = False
	pD = 0
	se_list = []
	for (d, m) in zip(diff, mark):
		if pD == 0 and d == 1:
			DeplicateFlag = m == 1
		if pD == 1 and d == 0:
			DeplicateFlag = False
		pD = d
		se_list.append(1 if DeplicateFlag else 0)
	return np.array(se_list)

def make():
	Sound_Element =  read_lab_file(LAB_FILE)
	Time_And_SElement = lab_to_graph(Sound_Element)

	fs, data = wavfile.read(WAV_FILE)
	pm_times, pm, f0_times, f0, corr = pyreaper.reaper_internal(data[:, 0].copy(order='C'), fs)
	calc_len = 0.005
	f_mark =np.empty((int)(len(data)/(calc_len*44100)))
	formants = np.empty(((int)(len(data)/(calc_len*44100)),3))
	data = data / 32768
	temp_f2 = 0
	for i in range((int)(len(data)/(calc_len*44100))):
		start_time = i*calc_len
		audio = data[(int)(start_time*44100):(int)(start_time*44100+calc_len*44100),0].astype(np.float)
		f = formant.calc_formant(audio, fs)
		if calc_volume(audio) > 0.05:
			formants[i] = [f[0], f[1] if len(f) > 2 else temp_f2, f[2] if len(f) > 3 else 0]
			if f[1] != 0:
				temp_f2 = f[1]
			f_mark[i]=1
		else:
			formants[i] = [0, 0, 0]
			f_mark[i]=0

	f_mark = needle_remover(f_mark,4)
	f1_diff = np.diff(formants[:, 0])
	f2_diff = np.diff(formants[:, 1])

	#EWMAで外れ値除外する

	f0_EWMA = EWMA_Filter(f0,10)
	f1_EWMA = EWMA_Filter(formants[:,0],10)
	f2_EWMA = EWMA_Filter(formants[:, 1], 10)

	f0_EWMA_30 = EWMA_Filter(f0, 30)
	f0_EWMA_50 = EWMA_Filter(f0, 50)

	f0_diff = np.diff(f0_EWMA)
	f0_change = f0_change_check(f0_diff)

	f_times = np.arange(0.0, len(data) / 44100, calc_len)
	#適当に生成してみるvsq4
	se_list = SoundElement_process(f0_change,f_mark[1:-2])
	

WAV_FILE = r"..\AnalyzeSystem\datas\STONES_ana.wav"
LAB_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\segmentation-kit\wav\STONES.lab"

if __name__ == "__main__":
	make()
