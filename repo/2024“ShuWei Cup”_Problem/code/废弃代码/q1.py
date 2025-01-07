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

# 定义低频和高频的功率谱密度模型
def low_freq_psd(f, P0, fc, q):
    """低频区域的功率谱密度模型"""
    return P0 / (1 + (f/fc)**q)

def high_freq_psd(f, A, alpha):
    """高频区域的功率谱密度模型"""
    return A * f**(-alpha)

# 获取并预处理数据
sampling_rate = 1/(time[1] - time[0])
frequencies, psd_values = compute_psd(detrended_residuals, sampling_rate)

# 分段频率
freq_split = 1e-3  # 分段点
low_freq_mask = frequencies < freq_split
high_freq_mask = frequencies >= freq_split

# 低频段拟合
low_freq = frequencies[low_freq_mask]
low_psd = psd_values[low_freq_mask]

P0_init = np.mean(low_psd)
initial_params_low = [P0_init, 1e-3, 2.0]
bounds_low = ([P0_init*0.1, 1e-4, 1.0],
              [P0_init*10, 1e-2, 4.0])

params_low, _ = curve_fit(low_freq_psd, low_freq, low_psd,
                         p0=initial_params_low,
                         bounds=bounds_low,
                         maxfev=10000)

P0, fc, q = params_low

# 高频段拟合
high_freq = frequencies[high_freq_mask]
high_psd = psd_values[high_freq_mask]

A_init = np.mean(high_psd) * (high_freq[0]**2)
initial_params_high = [A_init, 2.0]
bounds_high = ([A_init*0.1, 1.0],
               [A_init*10, 4.0])

params_high, _ = curve_fit(high_freq_psd, high_freq, high_psd,
                          p0=initial_params_high,
                          bounds=bounds_high,
                          maxfev=10000)

A, alpha = params_high

# 打印拟合结果
print("低频段拟合结果：")
print(f"P0 (红噪声强度) = {P0:.2e}")
print(f"fc (转角频率) = {fc:.2e}")
print(f"q (谱指数) = {q:.2f}")

print("\n高频段拟合结果：")
print(f"A (幅度) = {A:.2e}")
print(f"alpha (衰减指数) = {alpha:.2f}")

# 绘制拟合结果
plt.figure(figsize=(12, 8))
plt.loglog(frequencies, psd_values, 'b.', label="原始PSD", alpha=0.6)

# 绘制低频拟合结果
low_freq_fit = low_freq_psd(low_freq, P0, fc, q)
plt.loglog(low_freq, low_freq_fit, 'r-', label="低频拟合", linewidth=2)

# 绘制高频拟合结果
high_freq_fit = high_freq_psd(high_freq, A, alpha)
plt.loglog(high_freq, high_freq_fit, 'g-', label="高频拟合", linewidth=2)

plt.axvline(freq_split, color='k', linestyle='--', alpha=0.5, label='分段频率')

plt.xlabel("频率 (Hz)")
plt.ylabel("功率谱密度")
plt.title("分段拟合的功率谱密度")
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.show()

# 计算分段拟合的R²
def calculate_segment_r_squared(freq, true_psd, pred_psd):
    """计算分段R²"""
    y_true_log = np.log10(true_psd)
    y_pred_log = np.log10(pred_psd)
    residuals = y_true_log - y_pred_log
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_true_log - np.mean(y_true_log))**2)
    return 1 - (ss_res / ss_tot)

# 计算低频和高频段的R²
low_r2 = calculate_segment_r_squared(low_freq, low_psd, low_freq_fit)
high_r2 = calculate_segment_r_squared(high_freq, high_psd, high_freq_fit)

print(f"\n低频段拟合度 (R²): {low_r2:.4f}")
print(f"高频段拟合度 (R²): {high_r2:.4f}")
