# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, differential_evolution, minimize
from scipy.fft import fft, fftfreq
from scipy import signal
from tqdm import tqdm

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 从附件加载数据
file_path = r'C:\Users\tk\Desktop\2024“ShuWei Cup”_Problem\code\问题一\Attachment 1.xlsx'  # 文件路径
df = pd.ExcelFile(file_path)  # 读取Excel文件
data = df.parse(sheet_name=0)  # 加载第一个工作表

# 数据清理
cleaned_data = data.iloc[1:, [1, 0]]  # 提取第二列（MJD）和第三列（PT-TT）
cleaned_data.columns = ['MJD', 'PT_TT']  # 重命名列
cleaned_data = cleaned_data[pd.to_numeric(cleaned_data['MJD'], errors='coerce').notnull()]  # 去除非数值行
cleaned_data['MJD'] = cleaned_data['MJD'].astype(float)  # 转换为浮点型
cleaned_data['PT_TT'] = cleaned_data['PT_TT'].astype(float)  # 转换为浮点型

# 提取清理后的时间和残差数据
time = cleaned_data['MJD'].values
residuals = cleaned_data['PT_TT'].values

# 创建数据可视化图表
plt.figure(figsize=(10, 6), facecolor='white')
plt.plot(time, residuals, label='PT-TT', color='#1f77b4', linewidth=1.5)
plt.xlabel('修正儒略日 (MJD)', fontsize=12)
plt.ylabel('PT-TT (秒)', fontsize=12)
plt.title('PT和TT之间的时间差异', fontsize=14, pad=15)
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend(frameon=True, fontsize=10)
plt.tight_layout()
plt.show()

# 数据去趋势：使用更高阶多项式拟合去除长期趋势
def find_optimal_poly_order(time, residuals, max_order=10):
    """找到最优的多项式拟合阶数"""
    best_r2 = -np.inf
    best_order = 1
    
    for order in range(1, max_order + 1):
        poly_coeff = np.polyfit(time, residuals, order)
        trend = np.polyval(poly_coeff, time)
        r2 = 1 - np.sum((residuals - trend)**2) / np.sum((residuals - np.mean(residuals))**2)
        
        if r2 > best_r2:
            best_r2 = r2
            best_order = order
    
    return best_order

# 使用最优阶数进行拟合
optimal_order = find_optimal_poly_order(time, residuals)
poly_coeff = np.polyfit(time, residuals, optimal_order)
trend = np.polyval(poly_coeff, time)
detrended_residuals = residuals - trend

# 计算残差的功率谱密度
def compute_psd(detrended_residuals, sampling_rate=1):
    N = len(detrended_residuals)
    
    # 增加nperseg和noverlap参数的控制来获得更平滑的PSD估计
    nperseg = min(8192, N//2)  # 增加段长度
    noverlap = nperseg * 3//4  # 增加重叠率
    
    f, psd = signal.welch(detrended_residuals, 
                         fs=sampling_rate, 
                         window='hann',
                         nperseg=nperseg,
                         noverlap=noverlap,
                         detrend='linear')  # 添加线性去趋势
    
    # 只返回正频率部分
    mask = f > 0
    return f[mask], psd[mask]

# 定义功率谱密度（PSD）模型
def power_spectral_density(f, P0, fc, q):
    """
    改进的功率谱密度模型，增加了低频区域的拟合精度
    """
    return P0 / (1 + (f/fc)**q) + P0 * 1e-6  # 添加小偏移量避免零值

# 定义目标函数
def objective_function(params, frequencies, psd_values, freq_mask):
    P0, fc, q = params
    psd_pred = power_spectral_density(frequencies[freq_mask], P0, fc, q)
    y_true_log = np.log10(psd_values[freq_mask])
    y_pred_log = np.log10(psd_pred)
    weights = 1/frequencies[freq_mask]
    return np.sum(weights * (y_true_log - y_pred_log)**2)

# 获取并预处理数据
sampling_rate = 1/(time[1] - time[0])
frequencies, psd_values = compute_psd(detrended_residuals, sampling_rate)

# 设置优化参数范围
freq_mask = frequencies < 1e-2
P0_init = np.mean(psd_values[frequencies < 1e-3])
bounds = [(P0_init*0.01, P0_init*100), (1e-4, 1e-2), (1.0, 4.0)]

# 使用差分进化算法进行全局优化
print("正在进行差分进化全局优化...")
result_de = differential_evolution(
    objective_function,
    bounds,
    args=(frequencies, psd_values, freq_mask),
    maxiter=100,
    popsize=20,
    mutation=(0.5, 1.0),
    recombination=0.7,
    disp=True
)

# 使用Nelder-Mead算法进行局部优化
print("\n正在进行Nelder-Mead局部优化...")
result_nm = minimize(
    objective_function,
    result_de.x,
    args=(frequencies, psd_values, freq_mask),
    method='Nelder-Mead',
    options={'maxiter': 1000}
)

# 获取最终参数
P0, fc, q = result_nm.x

# 打印优化结果
print("\n最终拟合结果：")
print(f"P0 (红噪声强度) = {P0:.2e}")
print(f"fc (转角频率) = {fc:.2e}")
print(f"q (谱指数) = {q:.2f}")

# 绘制拟合结果和优化过程
plt.figure(figsize=(12, 8))

# 绘制原始数据和最终拟合结果
plt.subplot(211)
plt.loglog(frequencies, psd_values, label="原始PSD", color="blue", alpha=0.6)
plt.loglog(frequencies, power_spectral_density(frequencies, P0, fc, q),
          label="最优拟合", color="red", linestyle="--")
plt.axvline(fc, color='green', linestyle=':', alpha=0.5, label='转角频率')
plt.axhline(P0, color='orange', linestyle=':', alpha=0.5, label='噪声强度')
plt.xlabel("频率 (Hz)")
plt.ylabel("功率谱密度")
plt.title("优化后的红噪声功率谱密度拟合")
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)

# 计算并显示最终的R²值
def calculate_r_squared(frequencies, y_true, y_pred):
    """在低频区域计算R²"""
    freq_mask = frequencies < 1e-2
    y_true_log = np.log10(y_true[freq_mask])
    y_pred_log = np.log10(y_pred[freq_mask])
    residuals = y_true_log - y_pred_log
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_true_log - np.mean(y_true_log))**2)
    return 1 - (ss_res / ss_tot)

psd_fitted = power_spectral_density(frequencies, P0, fc, q)
r_squared = calculate_r_squared(frequencies, psd_values, psd_fitted)
print(f"\n最终模型拟合度 (R²): {r_squared:.4f}")

if r_squared >= 0.95:
    print("模型拟合度达到95%以上，符合要求。")
else:
    print("模型拟合度未达到95%，需要继续优化。")

plt.show()