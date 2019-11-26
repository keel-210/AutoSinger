# coding:utf-8
import wave
import numpy as np
import scipy.io.wavfile
import scipy.signal
from levinson_durbin import autocorr, LevinsonDurbin
import matplotlib.pyplot as plt

"""LPCスペクトル包絡を求める"""

def wavread(filename):
	wf = wave.open(filename, "r")
	fs = wf.getframerate()
	x = wf.readframes(wf.getnframes())
	x = np.frombuffer(x, dtype="int16") / 32768.0  # (-1, 1)に正規化
	wf.close()
	return x, float(fs)

def preEmphasis(signal, p):
	"""プリエンファシスフィルタ"""
	# 係数 (1.0, -p) のFIRフィルタを作成
	return scipy.signal.lfilter([1.0, -p], 1, signal)

def calc_formant(audio, fs):
	# 音声をロード
	wav=audio
	# t = np.arange(0.0, len(wav) / fs, 1/fs)

	# 音声波形の中心部分を切り出す
	# center = len(wav) / 2  # 中心のサンプル番号
	# cuttime = 0.04  # 切り出す長さ [s]
	# s = wav[(int)(center - cuttime/2*fs) : (int)(center + cuttime/2*fs)]
	s = wav
	
	# プリエンファシスフィルタをかける
	p = 0.97         # プリエンファシス係数
	s = preEmphasis(s, p)

	# ハミング窓をかける
	hammingWindow = np.hamming(len(s))
	s = s * hammingWindow

	# LPC係数を求める
	lpcOrder = 48
	r = autocorr(s, lpcOrder + 1)

	a, e = LevinsonDurbin(r, lpcOrder)
	
	# ----------------------------------------------------------------------
	# nfft = 2048
	# # FFTのサンプル数

	# fscale = np.fft.fftfreq(nfft, d = 1.0 / fs)[:(int)(nfft/2)]

	# # オリジナル信号の対数スペクトル
	# spec = np.abs(np.fft.fft(audio*hammingWindow, nfft))
	# logspec = 20 * np.log10(spec)
	# plt.plot(fscale, logspec[:(int)(nfft/2)])

	# # LPC対数スペクトル
	# w, h = scipy.signal.freqz(np.sqrt(e), a, nfft, "whole")
	# lpcspec = np.abs(h)
	# loglpcspec = 20 * np.log10(lpcspec)
	# plt.plot(fscale, loglpcspec[:(int)(nfft/2)], "r", linewidth=2)

	# plt.xlim((0, 4000))
	# plt.show()
	# ------------------------------------------------------------------------

	# フォルマント検出( by Tasuku SUENAGA a.k.a. gunyarakun )
	# 根を求めて三千里
	rts = np.roots(a)
	# 共役解のうち、虚部が負のものは取り除く
	rts = np.array(list(filter(lambda x: np.imag(x) >= 0, rts)))
	# 根から角度を計算
	angz = np.arctan2(np.imag(rts), np.real(rts))
	# 角度の低い順にソート
	sorted_index = angz.argsort()
	# 角度からフォルマント周波数を計算
	freqs = angz.take(sorted_index) * (fs / (2 * np.pi))
	# 角度からフォルマントの帯域幅も計算
	bw = -1 / 2 * (fs / (2 * np.pi)) * np.log(np.abs(rts.take(sorted_index)))

	ff=[]
	for i in range(len(freqs)):
		# フォルマントの周波数は90Hz超えで、帯域幅は400Hz未満
		if freqs[i] > 150 and bw[i] < 400 and freqs[i] < 3000:
			# print("formant : %d" % freqs[i])
			ff.append(freqs[i])
	return ff

if __name__ == "__main__":
	# 音声をロード
	wav, fs = wavread("a.wav")
	t = np.arange(0.0, len(wav) / fs, 1/fs)

	# 音声波形の中心部分を切り出す
	center = len(wav) / 2  # 中心のサンプル番号
	cuttime = 0.04         # 切り出す長さ [s]
	s = wav[center - cuttime/2*fs : center + cuttime/2*fs]

	# プリエンファシスフィルタをかける
	p = 0.97         # プリエンファシス係数
	s = preEmphasis(s, p)

	# ハミング窓をかける
	hammingWindow = np.hamming(len(s))
	s = s * hammingWindow

	# LPC係数を求める
	lpcOrder = 12
	r = autocorr(s, lpcOrder + 1)

	a, e  = LevinsonDurbin(r, lpcOrder)

	# フォルマント検出( by Tasuku SUENAGA a.k.a. gunyarakun )

	# 根を求めて三千里
	rts = np.roots(a)
	# 共役解のうち、虚部が負のものは取り除く
	rts = np.array(filter(lambda x: np.imag(x) >= 0, rts))

	# 根から角度を計算
	angz = np.arctan2(np.imag(rts), np.real(rts))
	# 角度の低い順にソート
	sorted_index = angz.argsort()
	# 角度からフォルマント周波数を計算
	freqs = angz.take(sorted_index) * (fs / (2 * np.pi))
	# 角度からフォルマントの帯域幅も計算
	bw = -1 / 2 * (fs / (2 * np.pi)) * np.log(np.abs(rts.take(sorted_index)))

	for i in range(len(freqs)):
		# フォルマントの周波数は90Hz超えで、帯域幅は400Hz未満
		if freqs[i] > 90 and bw[i] < 400:
			print("formant kita-: %d" % freqs[i])
