from scipy.io import wavfile
import pyworld as pw
import numpy as np
import matplotlib.pyplot as plt

WAV_FILE = "..\AnalyzeSystem\datas\wav\STONES_ana.wav"

# fs : sampling frequency, 音楽業界では44,100Hz
# data : arrayの音声データが入る 
fs, data = wavfile.read(WAV_FILE)

# floatでないとworldは扱えない
data = data.astype(np.float)

_f0, _time = pw.dio(data, fs)    # 基本周波数の抽出
f0 = pw.stonemask(data, _f0, _time, fs)  # 基本周波数の修正

# --- これは音声の合成に用いる(今回は使わない)
sp = pw.cheaptrick(data, f0, _time, fs)  # スペクトル包絡の抽出
# ap = pw.d4c(data, f0, _time, fs)         # 非周期性指標の抽出
# y = pw.synthesize(f0, sp, ap, fs)    # 合成


# 可視化
plt.plot(data, linewidth=1, color="blue", label="Raw Data")
plt.legend(fontsize=10)
plt.show()

plt.plot(f0, linewidth=1, color="green", label="F0 contour")
plt.legend(fontsize=10)
plt.show()

# plt.plot(sp, linewidth=1, color="red")
# plt.legend(fontsize=10)
# plt.show()