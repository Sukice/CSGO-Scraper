import datetime
import os
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import requests
from matplotlib import pyplot as plt

from cscraper.indicators import get_boll_n, get_rsi_n, get_rv_n, get_max_drawdown_n
from cscraper.csplot import plot_boll, plot_rsi, plot_rv
from cscraper.utils import get_random_headers, get_data_path, find_root

def get_cn_name(name = "梦魇武器箱"):
    timestamp = int(time.time() * 1000)
    url = f"https://api.steamdt.com/user/skin/v1/auto-completion?timestamp={timestamp}&content={name}"
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15)
        time.sleep(1.34)
        raw_data = response.json()
        def parse_data(raw_data):
            data = raw_data['data'][0]
            return data['name']
        return parse_data(raw_data)
    except Exception as e:
        print("url:"+url)
        print(e)


def get_data_csdt(name = "梦魇武器箱",mode = 'realtime'):
    name = get_cn_name(name)
    timestamp = int(time.time() * 1000)
    url = f"https://api.steamdt.com/skin/market/v3/page?timestamp={timestamp}"
    headers = {
        "Accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "access-token": "undefined",
        "content-type": "application/json",
        "language": "zh_CN",
        "origin": "https://steamdt.com",
        "referer": "https://steamdt.com/",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36 Edg/141.0.0.0",
        "x-app-version": "1.0.0",
        "x-currency": "CNY",
        "x-device": "1",
        "x-device-id": "6bbef8a8-34e9-429e-9279-1028e3524aa5"
    }
    payload = {
        "page": 1,
        "limit": 20,
        "dataField": "price",  # 示例：按价格字段筛选（可根据实际需求修改）
        "sortType": "asc",  # 示例：升序（asc=升序，desc=降序，根据接口支持的值调整）
        "queryName": name,
    }
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),  # 将字典转为 JSON 字符串
            timeout=10
        )
        time.sleep(1.24)
        response.raise_for_status()
        raw_data = response.json()
        def parse_realtime_data(raw_data, name):
            data = raw_data['data']['list']
            for item in data:
                if item['name'] == name:
                    price_dict = {}
                    price_dict['name'] = item['marketHashName']
                    data = item['sellingPriceList']
                    for single_data in data:
                        if single_data['platform'] in ['c5', 'buff', 'youpin']:
                            price_dict[single_data['platform']] = single_data['price']
                    price_dict['sellNum'] = item['sellNum']
                    price_dict['lowest_price'] = min(price_dict['c5'], price_dict['youpin'], price_dict['buff'])
                    df = pd.DataFrame([price_dict])
                    return df
            return None
        def parse_history_data(raw_data, name):
            data = raw_data['data']['list']
            for item in data:
                if item['name'] == name:
                    data = item['trendList']
                    df = pd.DataFrame(data, columns=['timestamp', 'price'])
                    df['date'] = df['timestamp'].apply(
                        lambda x: datetime.fromtimestamp(int(x)).strftime('%Y%m%d')
                    )

                    df['name'] = item['marketHashName']
                    df = df[['name','date', 'price']]
                    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                    today = datetime.today().date()
                    df = df[df['date'].dt.date < today]
                    df['date'] = df['date'].dt.strftime('%Y%m%d')
                    return df
            return None
        if mode == 'realtime':
            return parse_realtime_data(raw_data, name)
        elif mode == 'history':
            return parse_history_data(raw_data, name)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
    except requests.exceptions.ConnectionError:
        print("连接错误，请检查网络")
    except requests.exceptions.Timeout:
        print("请求超时")
    except json.JSONDecodeError:
        print("响应不是有效的 JSON 格式")
    except Exception as e:
        print(f"其他错误: {e}")
    return None

def get_realtime_data_csdt(name = "梦魇武器箱"):
    return get_data_csdt(name, mode = 'realtime')

def get_history_data_csdt(name = "梦魇武器箱"):
    return get_data_csdt(name, mode = 'history')



import matplotlib.dates as mdates
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
def brainstorm_cn(name, folder_path=os.path.join(get_data_path(), f"cn/brainstorm")):
    name = get_cn_name(name)
    file_name = name.replace(" ", "_")
    file_name = file_name.replace("|", "_")
    folder_path = os.path.join(folder_path, f"brainstorm_steam_of_{file_name}_{datetime.now().strftime('%Y%m%d')}")
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    count = 0
    filename = f"brainstorm_steam_of_{file_name}_{datetime.now().strftime('%Y%m%d')}.md"
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        pass

    # 表头
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write('\n# Brainstorm: \"' + name + '\" ( CN )\n')
        f.write('\n---\n')
        f.write(f'\n**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n')
        f.write("**数据来源**: CSDT\n\n")
        f.write("**分析周期**: 最近30天\n\n")

    start_date = datetime.now() - timedelta(days=30)
    start_date_str = start_date.strftime('%Y%m%d')

    df_realtime = get_realtime_data_csdt(name)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n---\n")
        f.write("\n## 📊 价格走势分析\n\n")
        f.write(f"### 今日实时行情 ( {datetime.now().strftime('%H:%M:%S')} )\n")
        if not df_realtime.empty:
            f.write("| c5 | buff | uusm | 在售数量 | 最低价 |\n")
            f.write("|------|--------|------|------|------|\n")
            for _, row in df_realtime.iterrows():
                f.write(f"| {row['c5']} | {row['buff']} | {row['youpin']} | {row['sellNum']} | {row['lowest_price']} |\n")
        f.write("\n")
    df_realtime_to_history = df_realtime
    df = get_history_data_csdt(name)
    today_data ={'date': datetime.now().strftime('%Y%m%d'),'name': df_realtime_to_history['name'].iloc[-1],'price':df_realtime_to_history['lowest_price'].iloc[-1]}
    new_row = pd.DataFrame([today_data])
    df = pd.concat([df, new_row], ignore_index=True)

    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df_history = df[df['date']>=start_date_str]
    if len(df_history) <25:
        print("该物品市场数据太少，无法提供有用数据")
        return
    df_history = df_history.copy()
    df_history['date'] = pd.to_datetime(df_history['date'].astype(str), format='%Y%m%d')
    # 创建子图，共享x轴，调整图像大小
    fig, ax1 = plt.subplots(figsize=(12, 7))
    ax1.plot(df_history['date'], df_history['price'], color='#2E86AB', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('价格', fontsize=13)
    ax1.set_title(f'近期价格分析', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.4)
    ax1.tick_params(axis='both', labelsize=11)
    date_format = mdates.DateFormatter('%Y-%m-%d')
    ax1.xaxis.set_major_formatter(date_format)
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=30)  # 调整日期旋转角度，使其更易读
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plt.savefig(chart_path, dpi=120, bbox_inches='tight')
    count += 1
    plt.close()

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("### 近期价格图表 (货币单位为CNY) \n")
        f.write(f'\n![价格走势图]({chart_name})\n\n')

    df = df.tail(50)

    df_boll = get_boll_n(df)
    df_boll = df_boll[df_boll['date']>=start_date_str]
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plot_boll(df_boll, chart_path, mode="compare", df_history=df_history)
    count += 1

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 📈 技术指标分析\n\n")
        f.write("### 20日布林带指标 & 20日移动均线 (Boll & MA20)\n")
        f.write(f'![布林带指标图]({chart_name})\n\n')
        f.write("### 20日相对强弱指数 (RSI20)\n")

    df_rsi = get_rsi_n(df)
    df_rsi = df_rsi[df_rsi['date']>=start_date_str]

    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plot_rsi(df_rsi, chart_path)
    count += 1

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f'![RSI指标图]({chart_name})\n\n')
        f.write("### 20日滚动波动率指标 (RV20)\n")

    df_rv = get_rv_n(df)
    df_rv = df_rv[df_rv['date']>=start_date_str]
    chart_name = f"chart{count}.png"
    chart_path = os.path.join(folder_path, chart_name)
    plot_rv(df_rv, chart_path)
    count += 1

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f'![RV20指标图]({chart_name})\n\n')

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

        f.write(f"| **流动性风险** | {liquidity_risk} | {liquidity_desc} |\n\n")

    root_dict = find_root(name)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 🔗 市场关联分析\n\n")
        f.write("### 物品来源追踪\n")
        f.write(f"**物品来源**: {root_dict['root']}\n\n")

        if not (root_dict['root'] is None) and not ('Capsule' in root_dict['root']):
            f.write("### 炼金关联分析\n")
            smaller_type = root_dict['brothers'].get(root_dict['type'] - 1, [])
            if root_dict['type'] != 6 and len(smaller_type) > 0:
                f.write("*炼金原料列表*\n\n")
                for item in smaller_type:
                    f.write(f"- {item}\n")

            bigger_type = root_dict['brothers'].get(root_dict['type'] + 1, [])
            if root_dict['type'] != 5 and len(bigger_type) > 0:
                f.write("\n*炼金成品列表*\n\n")
                for item in bigger_type:
                    f.write(f"- {item}\n")
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n## 🔍 多维分析建议\n\n")
        f.write("| 视角 | 关注重点 | 时间维度 | 风险偏好 |"
                "\n|------|----------|----------|----------|"
                "\n| **🎨 收藏价值** | 美学价值、稀有度、文化意义 | 长期 | 低风险 |"
                "\n| **🎮 实用价值** | 实用价值、视觉效果、使用体验 | 中期 | 中等风险 |"
                "\n| **💼 流动价值** | 流动性、波动规律、信息差 | 短期 | 高风险 |"
                "\n| **📈 投资价值** | 长期价值、趋势判断、资产配置 | 长期 | 中等风险 |\n\n")

        f.write("\n---\n")
        f.write("\n**报告生成完成**\n")
        f.write(f" *生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    print(f"报告已生成: {file_path}")


if __name__ == '__main__':
    brainstorm_cn("M4A1 | 次时代 （崭新出厂）")