import numpy as np
from scipy.io import wavfile
import pyreaper
import pandas as pd
import re
import vsq4_writer
import phonetic_symbol

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
	f.close()
	return time_and_soundele

def read_txt_file(path):
	f = open(path,encoding="UTF-8")
	l = f.read()
	l= [i for i in l]
	return l

def lab_to_ele(lab_list,txt_list):
	lab_vowel = np.array(lab_list)[:, 2]
	lab_string = ""
	for s in lab_vowel[1:-1]:
		lab_string += s + " "
	lab_vowel = re.split("(?<=[aiueo])", lab_string)
	lab_vowel = [phonetic_symbol.symbol4VOCALOID(l[1:]) if l[0] == " " else phonetic_symbol.symbol4VOCALOID(l) for l in lab_vowel if l != ""]
	print(lab_vowel)
	ele_list = [[t,l] for (l,t) in zip(lab_vowel, txt_list)]
	return np.array(ele_list)

def make_se_list(se_segment,se_time,se_ele):  #vsq4用の音素リストを作成する
	temp_i = 0
	SE_List = []
	for i in range(len(se_segment)):
		if (temp_i == 0 and se_segment[i] == 1) or (temp_i == 1 and se_segment[i] == 0):
			SE_List.append(se_time[i])
		temp_i = se_segment[i]
	t = [SE_List[idx:idx + 2] for idx in range(0,len(SE_List), 2)]
	SoundElement_And_Time = []
	for (i,e) in zip(t,se_ele):
		SoundElement_And_Time.append([i[0], i[1], e[0], e[1]])
	return SoundElement_And_Time

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
	Sound_Element = read_lab_file(LAB_FILE)
	ele_kana = read_txt_file(TXT_FILE)
	print(ele_kana)
	ele_list = lab_to_ele(Sound_Element,ele_kana)

	fs, data = wavfile.read(WAV_FILE)
	pm_times, pm, f0_times, f0, corr = pyreaper.reaper_internal(data[:, 0].copy(order='C'), fs)
	calc_len = 0.005
	f_mark =np.empty((int)(len(data)/(calc_len*44100)))
	data = data / 32768

	for i in range((int)(len(data)/(calc_len*44100))):
		start_time = i*calc_len
		audio = data[(int)(start_time * 44100):(int)(start_time * 44100 + calc_len * 44100), 0].astype(np.float)
		f_mark[i] = 1 if calc_volume(audio) > 0.05 else 0
	f_mark = needle_remover(f_mark,4)
	#EWMAで外れ値除外する

	f0_EWMA = EWMA_Filter(f0,10)

	f0_diff = np.diff(f0_EWMA)
	f0_change = f0_change_check(f0_diff)

	#適当に生成してみるvsq4
	se_list = SoundElement_process(f0_change,f_mark[1:-2])
	vsq4_list = make_se_list(f_mark[1:-2] - se_list, f0_times[1:], ele_list)
	print(vsq4_list)
	vsq4_writer.write_vsq4(VSQX_FILE,vsq4_list)

WAV_FILE = r"..\AnalyzeSystem\datas\STONES_ana.wav"
LAB_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\segmentation-kit\wav\STONES.lab"
TXT_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\segmentation-kit\wav\STONES.txt"
VSQX_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\test1_vsqx.vsqx"
if __name__ == "__main__":
	make()
