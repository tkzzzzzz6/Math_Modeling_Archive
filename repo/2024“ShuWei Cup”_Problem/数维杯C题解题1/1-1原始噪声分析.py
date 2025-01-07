import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
# 设置 matplotlib 使用支持中文和负号的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False    # 允许负号正常显示



# 读取Excel文件
file_path = '问题三附件数据.xlsx'
xls = pd.ExcelFile(file_path)
df = xls.parse(xls.sheet_names[0])

# 提取时间和信号列
time = pd.to_numeric(df['MJD(days)'], errors='coerce').dropna()
signal = pd.to_numeric(df['PT-TT（s）'], errors='coerce').dropna()

# 1. 时间特征分析
mean_signal = np.mean(signal)
std_signal = np.std(signal)
print("时间特征：")
print(f"信号平均值: {mean_signal}")
print(f"信号标准差: {std_signal}")

# 绘制时间域信号
plt.figure(figsize=(12, 6))
plt.plot(time, signal, color='blue')
plt.xlabel('时间 (天)')
plt.ylabel('计时残差 (秒)')
plt.title('时间域信号')
plt.grid()
plt.show()

# 2. 频域特征分析
N = len(signal)
sampling_rate = 1 / (time.iloc[1] - time.iloc[0])  # 假设时间间隔均匀
fft_values = fft(signal - mean_signal)
frequencies = fftfreq(N, d=1/sampling_rate)
psd = (np.abs(fft_values) ** 2) / N

# 绘制频谱图
plt.figure(figsize=(12, 6))
plt.loglog(frequencies[:N // 2], psd[:N // 2], color='red')
plt.xlabel('频率 (Hz)')
plt.ylabel('功率谱密度')
plt.title('信号的频谱特征')
plt.grid()
plt.show()

# 3. 自相关特征分析
autocorr = correlate(signal - mean_signal, signal - mean_signal, mode='full')
autocorr = autocorr[autocorr.size // 2:] / np.max(autocorr)  # 归一化并取正半部分

# 绘制自相关函数
plt.figure(figsize=(12, 6))
plt.plot(time[:len(autocorr)], autocorr, color='green')
plt.xlabel('滞后时间 (天)')
plt.ylabel('自相关')
plt.title('信号的自相关特征')
plt.grid()
plt.show()

# 4. 红噪声特征分析
# 低频区域特征，常见红噪声在低频区域会有较高功率密度
low_freq_threshold = 1e-4  # 可以根据实际数据情况调整
low_freq_indices = frequencies[:N // 2] < low_freq_threshold
low_freq_power = np.sum(psd[:N // 2][low_freq_indices])
total_power = np.sum(psd[:N // 2])
red_noise_ratio = low_freq_power / total_power

print("红噪声特征：")
print(f"低频区域（< {low_freq_threshold} Hz）功率占总功率的比例: {red_noise_ratio:.4f}")

if red_noise_ratio > 0.5:
    print("信号中可能存在显著的红噪声成分。")
else:
    print("信号中的红噪声成分不显著。")
