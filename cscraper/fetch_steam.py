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
def brainstorm_steam(name, folder_path="../data/steam/brainstorm"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    name = get_market_name(name)
    count = 0
    filename = f"brainstorm_steam_of_{name}_{datetime.now().strftime('%Y%m%d')}.md"
    file_path = os.path.join(folder_path, filename)

    # 初始化
    with open(file_path, 'w', encoding='utf-8') as f:
        pass

    # 表头
    with open(file_path, 'a', encoding='utf-8') as f:
        cn_name = convert_hash_to_ch(name)
        f.write('\n# Brainstorm: \"' + cn_name + '\" (Steam)\n')
        f.write('\n---\n')
        f.write(f'\n**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n')
        f.write("**数据来源**: Steam市场\n\n")
        f.write("**分析周期**: 最近30天\n\n")


    # 价格分析
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n---\n")
        f.write("\n## 📊 价格走势分析\n\n")
    df = get_history_data_steam(name)
    df_copy = df.tail(30).copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'].astype(str), format='%Y%m%d')
    plt.figure(figsize=(8, 4))
    df_copy.plot(x='date', y='price', kind='line')
    plt.tight_layout()
    chart_path = os.path.join(folder_path, f"chart{count}.png")
    plt.savefig(f'{chart_path}', dpi=100, bbox_inches='tight')
    count += 1
    plt.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        df_realtime = get_realtime_data_steam(name)
        f.write("### 今日实时行情\n")
        if not df_realtime.empty:
            f.write("| 价格 | 成交量 | 价格 | 价格 |\n")
            f.write("|------|--------|------|------|\n")
            for _, row in df_realtime.iterrows():
                f.write(f"| {row['median_price']} | {row['volume']} | {row['lowest_price']} | {row['number']} |\n")
        f.write("\n")

        f.write("### 近期价格图表\n")
        f.write(f'\n![价格走势图]({chart_path})\n')

    df = df.tail(40)

    print("近30天指标")
    df_ma = get_ma_n(df)
    df_ma = df_ma.tail(30)
    print(df_ma)
    df_rsi = get_rsi_n(df)
    df_rsi = df_rsi.tail(30)
    print(df_rsi)
    df_rv = get_rv_n(df)
    df_rv = df_rv.tail(30)
    print(df_rv)
    df_vol_ratio =  get_vol_ratio_n(df)
    df_vol_ratio = df_vol_ratio.tail(30)
    print(df_vol_ratio)



    df_boll = get_boll_n(df)
    df_boll = df_boll.tail(30)
    plt.figure(figsize=(10, 6))
    plt.plot(df_boll['date'], df_boll['upper'], label='上轨', alpha=0.7)
    plt.plot(df_boll['date'], df_boll['mid'], label='中轨', alpha=0.7)
    plt.plot(df_boll['date'], df_boll['lower'], label='下轨', alpha=0.7)
    plt.fill_between(df_boll['date'], df_boll['upper'], df_boll['lower'], alpha=0.2)
    plt.title(f'{cn_name} - 布林带指标')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = os.path.join(folder_path, f"chart{count}.png")
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    count += 1
    plt.close()

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("### 布林带指标 (Bollinger Bands)\n")
        f.write(f'![布林带指标图]({chart_path})\n\n')

    print("情绪异动")
    df_odd = df_rv[df_rv['RV20']>=1]
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 🔍 市场情绪分析\n\n")
        f.write("### 波动率指标 (RV)\n")
        chart_path = os.path.join(folder_path, f"chart{count}.png")
        f.write(f'![波动率指标图]({chart_path})\n\n')
        count += 1
        f.write("### 情绪异动检测\n")
        if not df_odd.empty:
            f.write("**检测到异常波动的日期**:\n")
            for _, row in df_odd.iterrows():
                f.write(f"- {row['date']} (RV20: {row['RV20']:.2f})\n")
        else:
            f.write("**近期未检测到显著情绪异动**\n")
        f.write("\n")


    print("近30天回撤情况")
    drawdown = get_max_drawdown_n(df,30)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## ⚠️ 风险指标\n\n")
        f.write("### 最大回撤分析\n")



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
        f.write(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    print(f"报告已生成: {file_path}")

if __name__ == "__main__":
    brainstorm_steam("Aces High Pin")


