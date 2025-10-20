import csv
import os
from datetime import datetime, timedelta
import requests
import re
import json
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup
import time

from cscraper.indicators import *
from cscraper.utils import get_random_headers, get_market_name, find_root, convert_hash_to_ch


def get_realtime_data_steam(
        name:str = "AK-47 | Bloodsport (Factory New)"
):
    name = get_market_name(name.strip())
    encoded_name = quote(name.encode('utf-8'))
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=23&market_hash_name={encoded_name}"
    response = requests.get(url, headers=get_random_headers(), timeout=15)
    time.sleep(1.34)
    data = response.json()
    url = f"https://steamcommunity.com/market/search?appid=730&currency=23&q={encoded_name}"
    response = requests.get(url, headers=get_random_headers())
    time.sleep(1.24)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        listing_number = soup.find('span', class_='market_listing_num_listings_qty')['data-qty']
        normal_price_text = soup.find('span', class_='normal_price', attrs={'data-price': True}).get_text(strip=True)
        print(f"正常价格：{normal_price_text}")
    else:
        print(f"请求失败，状态码：{response.status_code}")
    def parse_data(data):
        filtered_data = {
            'name': name,
            'lowest_price': data['lowest_price'],
            'volume': data['volume'],
            'median_price': data['median_price'],
            'number': listing_number,
        }
        df = pd.DataFrame([filtered_data])
        return df
    return parse_data(data)

def get_history_data_steam(
        name:str = "Dreams & Nightmares Case",
        mode:str = "raw"
):
    def parse_data_by_mode(df, mode):
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        if mode == "raw":
            df['amount'] = df['price'] * df['volume']
            date_agg = df.groupby('date', as_index=False).agg(
                all_volume=('volume', 'sum'),  # 同一日期的 volume 总和
                all_amount=('amount', 'sum')  # 同一日期的 amount 总和
            )
            df = pd.merge(df, date_agg, on='date', how='left')
            df['price'] = df['all_amount'] / df['all_volume']
            df = df[['date', 'name', 'price', 'all_volume']]
            df = df.rename(columns={
                'date': 'date',
                'name': 'name',
                'price': 'price',
                'all_volume': 'volume'
            })
            df = df.drop_duplicates(keep='first')
            df = df.reset_index(drop=True)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            today = datetime.today().date()
            df = df[df['date'].dt.date < today]
            df['date'] = df['date'].dt.strftime('%Y%m%d')
        return df

    name = get_market_name(name.strip())
    safe_name = name.replace("|", "-")
    if os.path.exists(f"../data/steam/{safe_name}.csv"):
        df = pd.read_csv(f"../data/steam/{safe_name}.csv")
        return parse_data_by_mode(df, mode)
    encoded_name = quote(name)
    url = f"https://steamcommunity.com/market/listings/730/{encoded_name}"
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15)
        time.sleep(1.64)
        response.raise_for_status()
        html_content = response.text
        pattern1 = r'var line1\s*=\s*(\[\[.*?\]\]);'
        match = re.search(pattern1, html_content, re.DOTALL)
        if match:
            data_str = match.group(1)
            try:
                data = json.loads(data_str)
                df = pd.DataFrame(data, columns=['raw_date', 'price', 'volume'])
                def parse_date(date_str):
                    date_part = date_str[:11].strip()
                    dt = datetime.strptime(date_part, '%b %d %Y')
                    return dt.strftime('%Y%m%d')
                df['date'] = df['raw_date'].apply(parse_date)
                df['name'] = name
                df = df[['date', 'name', 'price', 'volume']]
                if not os.path.exists(f"../data/steam"):
                    os.makedirs("../data/steam", exist_ok=True)
                filename = f"../data/steam/{name}.csv"
                safe_name = filename.replace("|", "-")
                df.to_csv(safe_name, index=False, quoting=csv.QUOTE_NONNUMERIC)
                return parse_data_by_mode(df, mode)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return None
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
def brainstorm_steam(name, folder_path="../data/steam/brainstorm"):
    name = get_market_name(name).strip()
    file_name = name.replace(" ", "_")
    folder_path = os.path.join(folder_path, f"brainstorm_steam_of_{file_name}_{datetime.now().strftime('%Y%m%d')}")
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    count = 0
    filename = f"brainstorm_steam_of_{file_name}_{datetime.now().strftime('%Y%m%d')}.md"
    file_path = os.path.join(folder_path, filename)

    # 初始化
    with open(file_path, 'w', encoding='utf-8') as f:
        pass

    # 表头
    with open(file_path, 'a', encoding='utf-8') as f:
        cn_name = convert_hash_to_ch(name)
        f.write('\n# Brainstorm: \"' + cn_name + '\" ( Steam )\n')
        f.write('\n---\n')
        f.write(f'\n**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n')
        f.write("**数据来源**: Steam市场\n\n")
        f.write("**分析周期**: 最近30天\n\n")


    # 价格分析
    df_realtime = get_realtime_data_steam(name)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n---\n")
        f.write("\n## 📊 价格走势分析\n\n")
        f.write(f"### 今日实时行情 ( {datetime.now().strftime('%H:%M:%S')} )\n")
        if not df_realtime.empty:
            f.write("| 最低价格 | 平均价格 | 成交量 | 在售数量 |\n")
            f.write("|------|--------|------|------|\n")
            for _, row in df_realtime.iterrows():
                f.write(f"| {row['lowest_price']} | {row['median_price']} | {row['volume']} | {row['number']} |\n")
        f.write("\n")

    df = get_history_data_steam(name)


    df_history = df.tail(30).copy()
    df_history['date'] = pd.to_datetime(df_history['date'].astype(str), format='%Y%m%d')
    # 创建子图，共享x轴，调整图像大小
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    # 上图：价格走势线图
    ax1.plot(df_history['date'], df_history['price'], color='#2E86AB', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('价格', fontsize=13)
    ax1.set_title(f'{cn_name} - 近期价格与成交量分析', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.4)
    ax1.tick_params(axis='both', labelsize=11)
    # 下图：成交量直方图
    ax2.bar(df_history['date'], df_history['volume'], color='#A23B72', alpha=0.7, width=0.8)
    ax2.set_ylabel('成交量', fontsize=13)
    ax2.set_xlabel('日期', fontsize=13)
    ax2.grid(True, alpha=0.4)
    ax2.tick_params(axis='both', labelsize=11)

    # 设置x轴日期格式，更细化显示
    date_format = mdates.DateFormatter('%Y-%m-%d')
    ax2.xaxis.set_major_formatter(date_format)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # 每天显示一个刻度
    plt.xticks(rotation=30)  # 调整日期旋转角度，使其更易读

    # 调整子图之间的间距以及子图与边框的间距
    plt.subplots_adjust(hspace=0.1, left=0.1, right=0.95, top=0.9, bottom=0.1)

    # 保存图像
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=120, bbox_inches='tight')
    count += 1
    plt.close()

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("### 近期价格图表 (按当前IP地址选择货币单位) \n")
        f.write(f'\n![价格走势图]({chart_name})\n\n')


    df = df.tail(40)

    df_boll = get_boll_n(df)
    df_boll = df_boll.tail(30)
    df_boll['date'] = pd.to_datetime(df_boll['date'].astype(str), format='%Y%m%d')
    # 创建画布和子图，设置更合适的大小
    fig, ax = plt.subplots(figsize=(12, 7))
    # 绘制上轨、中轨、下轨，设置更美观的颜色和线条样式
    ax.plot(df_boll['date'], df_boll['upper'], label='上轨', color='#1f77b4', linewidth=2, linestyle='-')
    ax.plot(df_boll['date'], df_boll['mid'], label='中轨/MA20', color='#ff7f0e', linewidth=2, linestyle='-')
    ax.plot(df_boll['date'], df_boll['lower'], label='下轨', color='#2ca02c', linewidth=2, linestyle='-')
    ax.plot(df_history['date'], df_history['price'], label='实际价格', color='#d62728', linewidth=2, linestyle='-')
    # 填充上轨和下轨之间的区域，设置更柔和的颜色
    ax.fill_between(df_boll['date'], df_boll['upper'], df_boll['lower'], color='#e6f7ff', alpha=0.3)
    # 设置标题，增大字号并加粗
    ax.set_title(f'{cn_name} - 20日布林带指标', fontsize=16, fontweight='bold')
    # 设置坐标轴标签，增大字号
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('价格', fontsize=12)
    # 设置图例，位置更合理
    ax.legend(loc='upper left', fontsize=10)
    # 设置x轴日期格式，更细化且美观
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # 每2天显示一个刻度
    plt.xticks(rotation=30)  # 调整日期旋转角度，更易读
    # 添加网格，增强可读性
    ax.grid(True, linestyle='--', alpha=0.5)
    # 调整布局，避免元素重叠
    plt.tight_layout()

    # 保存图像
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')  # 提高dpi，让图像更清晰
    count += 1
    plt.close()

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 📈 技术指标分析\n\n")
        f.write("### 20日布林带指标 & 20日移动均线 (Bollinger Bands & MA20)\n")
        f.write(f'![布林带指标图]({chart_name})\n\n')
        f.write("### 20日相对强弱指数 (RSI20)\n")

    df_rsi = get_rsi_n(df)
    df_rsi = df_rsi.tail(30)
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
    ax.set_title(f'{cn_name} - 20日相对强弱指数(RSI)', fontsize=16, fontweight='bold')

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

    # 保存图像，提高dpi让图像更清晰
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    count += 1
    plt.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f'![RSI指标图]({chart_name})\n\n')
        f.write("### 20日量比 (Volume Ratio)\n")

    df_vol_ratio = get_vol_ratio_n(df)
    df_vol_ratio = df_vol_ratio.tail(30)
    df_vol_ratio['date'] = df_vol_ratio['date'] = pd.to_datetime(df_vol_ratio['date'].astype(str), format='%Y%m%d')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_vol_ratio['date'], df_vol_ratio['VR20'], label='VR20', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)

    ax.axhline(y=3, color='r', linestyle='--', alpha=0.6, label='狂热(3)')
    ax.axhline(y=1.5, color='g', linestyle='-.', alpha=0.5, label='正常(1.5)')
    ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.6, label='低迷(0.8)')

    # 设置标题，增大字号并加粗
    ax.set_title(f'{cn_name} - 20日量比(VR20)', fontsize=16, fontweight='bold')
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
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    count += 1
    plt.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f'![VR指标图]({chart_name})\n\n')
        f.write("### 20日滚动波动率指标 (Rolling Volatility)\n")

    df_rv = get_rv_n(df)
    df_rv = df_rv.tail(30)
    df_rv['date'] = df_rv['date'] = pd.to_datetime(df_rv['date'].astype(str), format='%Y%m%d')
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(df_rv['date'], df_rv['RV20'], label='RV20', color='#1f77b4', linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.8)

    # 设置标题，增大字号并加粗
    ax.set_title(f'{cn_name} - 20日滚动波动率(RV20)', fontsize=16, fontweight='bold')
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
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    count += 1
    plt.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f'![RV20指标图]({chart_name})\n\n')

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 🔍 市场情绪分析\n\n")
        f.write("待更新\n\n")

    drawdown_result = get_max_drawdown_n(df, 30)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## ⚠️ 风险指标\n\n")
        f.write("### 最大回撤分析\n")
        # 最大回撤详细表格
        f.write("#### 最大回撤详细信息\n")
        f.write("| 指标 | 数值 | 说明 |\n")
        f.write("|------|------|------|\n")
        f.write(f"| **最大回撤幅度** | {abs(drawdown_result['max_drawdown']):.2f}% | 从峰值到谷值的最大跌辐 |\n")
        f.write(f"| **峰值日期** | {drawdown_result['max_drawdown_peak_date']} | 回撤开始前的最高点 |\n")
        f.write(f"| **峰值价格** | {drawdown_result['max_drawdown_peak_price']:.2f} | 回撤开始前的最高价格 |\n")
        f.write(f"| **谷值日期** | {drawdown_result['max_drawdown_trough_date']} | 回撤结束的最低点 |\n")
        f.write(f"| **谷值价格** | {drawdown_result['max_drawdown_trough_price']:.2f} | 回撤结束的最低价格 |\n")
        f.write(
            f"| **价格下跌** | {drawdown_result['max_drawdown_peak_price'] - drawdown_result['max_drawdown_trough_price']:.2f} | 从峰值到谷值的绝对跌值 |\n")

        # 回撤恢复情况表格
        f.write("\n#### 回撤恢复情况\n")
        f.write("| 指标 | 状态 | 说明 |\n")
        f.write("|------|------|----------|\n")

        recovery_status = "✅ 已恢复" if drawdown_result['recovery_success'] else "❌ 未恢复"
        f.write(f"| **恢复状态** | {recovery_status} | 价格是否回到峰值水平 |\n")

        if drawdown_result['recovery_success']:
            f.write(f"| **恢复天数** | {drawdown_result['recovery_days']}天 | 从谷值恢复到峰值所需时间 |\n")
            f.write(f"| **恢复日期** | {drawdown_result['recovery_date']} | 价格回到峰值的日期 |\n")
        else:
            f.write(f"| **恢复天数** | - | 尚未恢复到峰值水平 |\n")
            f.write(f"| **恢复日期** | - | 尚未恢复到峰值水平 |\n")

        # 风险等级评估
        f.write("\n#### 风险等级评估\n")
        f.write("| 评估维度 | 等级 | 说明 |\n")
        f.write("|----------|------|------|\n")

        # 根据回撤幅度评估风险等级
        drawdown_percent = abs(drawdown_result['max_drawdown'])
        if drawdown_percent < 5:
            risk_level = "🟢 低风险"
            risk_desc = "回撤幅度较小，风险可控"
        elif drawdown_percent < 10:
            risk_level = "🟡 中风险"
            risk_desc = "回撤幅度适中，需关注"
        elif drawdown_percent < 20:
            risk_level = "🟠 高风险"
            risk_desc = "回撤幅度较大，谨慎操作"
        else:
            risk_level = "🔴 极高风险"
            risk_desc = "回撤幅度很大，风险极高"

        f.write(f"| **回撤风险** | {risk_level} | {risk_desc} |\n")

        # 根据恢复情况评估流动性风险
        if drawdown_result['recovery_success']:
            liquidity_risk = "🟢 流动性良好"
            liquidity_desc = "价格能够快速恢复，流动性较好"
        else:
            liquidity_risk = "🟡 流动性一般"
            liquidity_desc = "价格恢复较慢，流动性需关注"

        f.write(f"| **流动性风险** | {liquidity_risk} | {liquidity_desc} |\n")

        f.write("\n")



    dict = find_root(name)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 🔗 市场关联分析\n\n")
        f.write("### 物品来源追踪\n")
        f.write(f"**物品来源**: {dict['root']}\n\n")


        if not 'Capsule' in dict['root']:
            f.write("### 炼金原料关联分析\n")
            f.write("*炼金原料市场走势分析待完善*\n\n")

    # 总结部分
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 💡 投资建议\n\n")
        f.write("### 短期展望 (1-7天)\n")
        f.write("*基于技术指标的短期分析待完善*\n\n")

        f.write("### 中期展望 (7-30天)\n")
        f.write("*基于趋势和基本面的中期分析待完善*\n\n")

        f.write("### 风险提示\n")
        f.write("1. 市场波动风险\n")
        f.write("2. 流动性风险\n")
        f.write("3. 政策风险\n\n")

        f.write("---\n")
        f.write("\n**报告生成完成**\n")
        f.write(f" *生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    print(f"报告已生成: {file_path}")

if __name__ == "__main__":
    brainstorm_steam("Aces High Pin")


