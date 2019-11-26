from pydub import AudioSegment

# mp3ファイルの読み込み
sound = AudioSegment.from_file("../AnalyzeSystem/datas/vocals.wav", format="wav")

sound1 = sound[20000:26000]

# 抽出した部分を出力
sound1.export("output1.wav", format="wav")