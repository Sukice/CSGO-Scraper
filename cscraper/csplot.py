import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

def plot_boll(df_boll, chart_path, mode="simple", df_history=None):
    df_boll['date'] = pd.to_datetime(df_boll['date'].astype(str), format='%Y%m%d')

    # 创建画布和子图，设置更合适的大小
    fig, ax = plt.subplots(figsize=(12, 7))
    # 绘制上轨、中轨、下轨，设置更美观的颜色和线条样式
    ax.plot(df_boll['date'], df_boll['upper'], label='上轨', color='#1f77b4', linewidth=2, linestyle='-')
    ax.plot(df_boll['date'], df_boll['mid'], label='中轨/MA20', color='#ff7f0e', linewidth=2, linestyle='-')
    ax.plot(df_boll['date'], df_boll['lower'], label='下轨', color='#2ca02c', linewidth=2, linestyle='-')
    if mode != 'simple':
        if df_history is None:
            raise ValueError("df_history is None")
        ax.plot(df_history['date'], df_history['price'], label='实际价格', color='#d62728', linewidth=2, linestyle='-')

    # 填充上轨和下轨之间的区域，设置更柔和的颜色
    ax.fill_between(df_boll['date'], df_boll['upper'], df_boll['lower'], color='#e6f7ff', alpha=0.3)
    # 设置标题，增大字号并加粗
    ax.set_title(f'20日布林带指标', fontsize=16, fontweight='bold')
    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('价格', fontsize=12)
    # 设置图例，位置更合理
    ax.legend(loc='upper left', fontsize=10)
    # 设置x轴日期格式，更细化且美观
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=30)

    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()

    plt.savefig(chart_path, dpi=150, bbox_inches='tight')  # 提高dpi，让图像更清晰
    plt.close()

def plot_rsi(df_rsi, chart_path):
    df_rsi['date'] = pd.to_datetime(df_rsi['date'].astype(str), format='%Y%m%d')

    # 创建画布和子图，设置更合适的大小
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_rsi['date'], df_rsi['RSI20'], label='RSI6', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)

    # 绘制超买超卖线，设置更柔和的样式
    ax.axhline(y=70, color='r', linestyle='--', alpha=0.6, label='超买线(70)')
    ax.axhline(y=30, color='g', linestyle='--', alpha=0.6, label='超卖线(30)')
    # 绘制50中轨线，辅助判断趋势
    ax.axhline(y=50, color='gray', linestyle='-.', alpha=0.5, label='中轨(50)')

    # 设置标题，增大字号并加粗
    ax.set_title(f'20日相对强弱指数(RSI)', fontsize=16, fontweight='bold')

    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('RSI值', fontsize=12)

    # 设置图例，位置更合理且显示更美观
    ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='gray')

    # 设置x轴日期格式，更细化且美观
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # 每2天显示一个刻度
    plt.xticks(rotation=30)  # 调整日期旋转角度，更易读

    # 添加网格，增强可读性
    ax.grid(True, linestyle='--', alpha=0.3, color='gray')

    # 设置y轴范围，让图表更紧凑
    ax.set_ylim(0, 100)

    # 调整布局，避免元素重叠
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_vr(df_vol_ratio, chart_path):
    df_vol_ratio['date'] = df_vol_ratio['date'] = pd.to_datetime(df_vol_ratio['date'].astype(str), format='%Y%m%d')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_vol_ratio['date'], df_vol_ratio['VR20'], label='VR20', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)

    ax.axhline(y=3, color='r', linestyle='--', alpha=0.6, label='狂热(3)')
    ax.axhline(y=1.5, color='g', linestyle='-.', alpha=0.5, label='正常(1.5)')
    ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.6, label='低迷(0.8)')

    # 设置标题，增大字号并加粗
    ax.set_title(f'20日量比(VR20)', fontsize=16, fontweight='bold')
    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('VR值', fontsize=12)
    # 设置图例，位置更合理且显示更美观
    ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='gray')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=30)
    ax.grid(True, linestyle='--', alpha=0.3, color='gray')
    # 调整布局，避免元素重叠
    plt.tight_layout()
    # 保存图像，提高dpi让图像更清晰
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_rv(df_rv, chart_path):
    df_rv['date'] = df_rv['date'] = pd.to_datetime(df_rv['date'].astype(str), format='%Y%m%d')
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_rv['date'], df_rv['RV20'], label='RV20', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)
    # 设置标题，增大字号并加粗
    ax.set_title(f'20日滚动波动率(RV20)', fontsize=16, fontweight='bold')
    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('RV值', fontsize=12)
    # 设置图例，位置更合理且显示更美观
    ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='gray')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=30)
    ax.grid(True, linestyle='--', alpha=0.3, color='gray')
    # 调整布局，避免元素重叠
    plt.tight_layout()
    # 保存图像，提高dpi让图像更清晰
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_ma(df_ma, chart_path):
    df_ma['date'] = df_ma['date'] = pd.to_datetime(df_ma['date'].astype(str), format='%Y%m%d')
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_ma['date'], df_ma['RV20'], label='RV20', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)
    # 设置标题，增大字号并加粗
    ax.set_title(f'20日移动平均线(MA20)', fontsize=16, fontweight='bold')
    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('MA值', fontsize=12)
    # 设置图例，位置更合理且显示更美观
    ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='gray')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=30)
    ax.grid(True, linestyle='--', alpha=0.3, color='gray')
    # 调整布局，避免元素重叠
    plt.tight_layout()
    # 保存图像，提高dpi让图像更清晰
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()