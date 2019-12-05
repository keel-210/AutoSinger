import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import pyreaper
import pandas as pd
import pyworld as pw
from scipy.signal import lfilter

def calc_volume(data):
	v=0.0
	for x in data:
		v += abs(x)
	v = v / len(data)
	return v

def EWMA_Filter(target,ewm_span):
	ewm_mean = EWMA(target,0.15)
	return np.array(ewm_mean)

def zero_fill(x):
	temp_i = 0
	for i in x:
		if temp_i != 0 and i == 0:  #立下り
			return
			
def EWMA(x, alpha):
    y,_ = lfilter([alpha], [1,alpha-1], x, zi=[x[0]*(1-alpha)])
    return y

def read_lab_file(path): #labファイルを配列に
	f = open(path)
	l = f.read().split("\n")
	time_and_soundele = []
	for i in l:
		tas = i.split(" ")
		if len(tas) == 3:
			time_and_soundele.append([float(tas[0]), float(tas[1]), tas[2]])
	return time_and_soundele

def needle_remover(l,needle_size): #突出値除外
	for i in range(len(l) - (needle_size + 2) + 1):
		if l[i] < l[i+1] and l[i+needle_size] > l[i + needle_size + 1]:
			l[i + 1:i + needle_size+1] = [(l[i] + l[i + needle_size + 1]) / 2]*needle_size
	return l
def needle_remover_binary(l,needle_size): #突出値除外
	for i in range(len(l) - (needle_size + 2) + 1):
		if l[i] == l[i + needle_size + 1]:
			l[i + 1:i + needle_size+1] = [(l[i] + l[i + needle_size + 1]) / 2]*needle_size
	return l
def f0_change_check(diff):
	change_list = [0 if abs(d) <= 5 else 1 for d in diff]
	needle_remover_binary(change_list,1)
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

def tekitou_window(x, ave_len):
	y = [np.average(np.array(x[int(i - ave_len / 2) if i > ave_len / 2 else 0:int(i + ave_len / 2) if i + ave_len / 2 < len(x) else len(x) - 1])
	*np.hamming(-(int(i-ave_len/2) if i > ave_len/2 else 0) + (int(i+ave_len/2) if i+ave_len/2 < len(x) else len(x)-1))) for i in range(len(x)) ]
	return np.array(y)/np.max(y)

def main(s_time,e_time):
	WAV_FILE = r"C:\Users\KEEL\Documents\GitHub\AutoSinger\AnalyzeSystem\datas\STONES_vocals.wav"

	fs, data = wavfile.read(WAV_FILE)
	data = data[s_time*fs:e_time*fs]
	
	data = data.astype(np.float)
	_f0, _time = pw.dio(data[:,0].copy(order='C'), fs)    # 基本周波数の抽出
	f0 = pw.stonemask(data[:, 0].copy(order='C'), _f0, _time, fs)  # 基本周波数の修正
	print(np.shape(f0))

	calc_len = 0.005
	f0_times = np.arange(float(s_time),float(e_time),calc_len)
	f_mark =np.empty((int)(len(data)/(calc_len*fs)))
	data = data / 32768
	for i in range((int)(len(data)/(calc_len*fs))):
		start_time = i*calc_len
		audio = data[(int)(start_time * fs):(int)(start_time * fs + calc_len * fs), 0].astype(np.float)
		f_mark[i] = 1 if calc_volume(audio) > 0.05 else 0
	f_mark = needle_remover_binary(f_mark, 4)
	
	temp_f = 0
	zf_f0 = []
	for (f, m) in zip(f0, f_mark):
		if m == 1:
			if f == 0:
				zf_f0.append(temp_f)
			else:
				zf_f0.append(f)
				temp_f = f
		else:
			zf_f0.append(0)
	zf_f0.append(0)
	f0 = np.array(zf_f0)
	print(np.shape(f0))
	f0_EWMA = EWMA_Filter(f0,10)
	f0_diff = np.diff(f0_EWMA)
	f0_diff = np.array([d if m != 0 and abs(d) < 10 else 0 for (d, m) in zip(f0_diff, f_mark)])
	f0_diff = needle_remover(f0_diff,1)
	f0_diff = needle_remover(f0_diff,4)
	f0_change = f0_change_check(f0_diff)
	se_list = SoundElement_process(f0_change, f_mark)
	# se_list = needle_remover(se_list, 4)
	
	print(np.shape(f0_times))
	print(np.shape(f_mark))
	print(np.shape(se_list))

	plt.plot(f0_times, f_mark*5)
	# plt.plot(f0_times, f0_EWMA[1:])
	plt.plot(f0_times, f0_diff)
	plt.plot(f0_times,f0_change)
	#遷移部と平坦部分が存在する
	# plt.plot(f0_times, f0_change*75)
	# plt.plot(f0_times, (f_mark - se_list) * 50)
	plt.show()

if __name__ == "__main__":
	main(20,30)