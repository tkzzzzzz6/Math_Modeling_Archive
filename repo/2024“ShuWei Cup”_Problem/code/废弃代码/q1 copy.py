import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.fft import fft, fftfreq
from scipy import signal

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 从附件加载数据
file_path = 'q1/Attachment 1.xlsx'  # 文件路径
df = pd.ExcelFile(file_path)  # 读取Excel文件
data = df.parse(sheet_name=0)  # 加载第一个工作表

# 数据清理
cleaned_data = data.iloc[1:, [1, 2]]  # 提取第二列（MJD）和第三列（PT-TT）
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

# 获取并预处理数据
sampling_rate = 1/(time[1] - time[0])
frequencies, psd_values = compute_psd(detrended_residuals, sampling_rate)

# 数据分段
low_freq_mask = frequencies < 1e-3
high_freq_mask = frequencies >= 1e-3

# 估计初始参数
P0_init = np.mean(psd_values[low_freq_mask])  # 使用低频区平均值作为P0初始值
fc_init = 1e-3  # 从图像观察到的转角频率
q_init = 2.0    # 初始谱指数

# 设置参数边界
initial_params = [P0_init, fc_init, q_init]
bounds = ([P0_init*0.1, 1e-4, 1.0],  # 下界
          [P0_init*10, 1e-2, 4.0])   # 上界

# 拟合
params, covariance = curve_fit(power_spectral_density, frequencies, psd_values,
                             p0=initial_params, bounds=bounds, maxfev=10000,
                             method='trf')  # 使用 trust region reflective 算法

P0, fc, q = params

# 打印拟合结果
print(f"拟合结果：")
print(f"P0 (红噪声强度) = {P0:.2e}")
print(f"fc (转角频率) = {fc:.2e}")
print(f"q (谱指数) = {q:.2f}")

# 绘制拟合结果
plt.figure(figsize=(10, 6))
plt.loglog(frequencies, psd_values, label="原始PSD", color="blue", alpha=0.6)
plt.loglog(frequencies, power_spectral_density(frequencies, P0, fc, q),
          label="拟合PSD", color="red", linestyle="--")

# 添加辅助线
plt.axvline(fc, color='green', linestyle=':', alpha=0.5, label='转角频率')
plt.axhline(P0, color='orange', linestyle=':', alpha=0.5, label='噪声强度')

plt.xlabel("频率 (Hz)")
plt.ylabel("功率谱密度")
plt.title("改进的红噪声功率谱密度拟合")
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.show()

# 计算模型拟合度（R²）
def calculate_r_squared(frequencies, y_true, y_pred):
    """改进的R²计算方法"""
    freq_mask = frequencies < 1e-2
    
    # 使用对数尺度计算R²
    y_true_log = np.log10(y_true[freq_mask])
    y_pred_log = np.log10(y_pred[freq_mask])
    
    # 使用加权残差
    weights = 1/frequencies[freq_mask]
    weighted_residuals = (y_true_log - y_pred_log) * np.sqrt(weights)
    weighted_mean = np.average(y_true_log, weights=weights)
    
    ss_res = np.sum(weighted_residuals**2)
    ss_tot = np.sum(((y_true_log - weighted_mean) * np.sqrt(weights))**2)
    
    return 1 - (ss_res / ss_tot)

# 计算R²
psd_fitted = power_spectral_density(frequencies, P0, fc, q)
r_squared = calculate_r_squared(frequencies, psd_values, psd_fitted)
print(f"模型拟合度 (R²): {r_squared:.4f}")

# 提示是否达到95%的拟合度
if r_squared >= 0.95:
    print("模型拟合度达到95%以上，符合要求。")
else:
    print("模型拟合度未达到95%，需要优化。")

def segment_analysis(frequencies, psd_values, segment_size=1000):
    """对数据进行分段分析以提高拟合精度"""
    segments = []
    for i in range(0, len(frequencies), segment_size):
        end = min(i + segment_size, len(frequencies))
        segment_freq = frequencies[i:end]
        segment_psd = psd_values[i:end]
        
        # 对每个段进行单独拟合
        try:
            params, _ = curve_fit(power_spectral_density, segment_freq, segment_psd,
                                p0=initial_params, bounds=bounds, maxfev=10000)
            segments.append((segment_freq, segment_psd, params))
        except:
            continue
    
    return segments

# 修改拟合策略，主要关注低频区域
def fit_psd_model(frequencies, psd_values):
    # 对数据进行预处理
    freq_mask = frequencies < 1e-2
    
    # 对数据进行平滑处理
    smooth_psd = signal.savgol_filter(np.log10(psd_values), 
                                    window_length=11, 
                                    polyorder=3)
    smooth_psd = 10**smooth_psd
    
    # 使用选定区域的数据进行拟合
    P0_init = np.mean(psd_values[frequencies < 1e-3])
    initial_params = [P0_init, 1e-3, 2.0]
    bounds = ([P0_init*0.01, 1e-4, 1.0],  # 扩大参数范围
              [P0_init*100, 1e-2, 4.0])
    
    # 使用加权最小二乘拟合
    weights = 1/frequencies[freq_mask]  # 给低频区域更高的权重
    
    params, _ = curve_fit(power_spectral_density, 
                         frequencies[freq_mask], 
                         smooth_psd[freq_mask],
                         p0=initial_params, 
                         bounds=bounds,
                         sigma=weights,
                         maxfev=10000,
                         method='trf')
    
    return params

# 应用修改后的函数
frequencies, psd_values = compute_psd(detrended_residuals, sampling_rate)
P0, fc, q = fit_psd_model(frequencies, psd_values)

# 计算R²时只考虑低频区域
def calculate_r_squared(frequencies, y_true, y_pred):
    """在低频区域计算R²"""
    freq_mask = frequencies < 1e-2
    y_true_log = np.log10(y_true[freq_mask])
    y_pred_log = np.log10(y_pred[freq_mask])
    residuals = y_true_log - y_pred_log
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_true_log - np.mean(y_true_log))**2)
    return 1 - (ss_res / ss_tot)

# 计算R²
psd_fitted = power_spectral_density(frequencies, P0, fc, q)
r_squared = calculate_r_squared(frequencies, psd_values, psd_fitted)
print(f"模型拟合度 (R²): {r_squared:.4f}")

# 提示是否达到95%的拟合度
if r_squared >= 0.95:
    print("模型拟合度达到95%以上，符合要求。")
else:
    print("模型拟合度未达到95%，需要优化。")