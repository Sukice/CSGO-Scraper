import os
from datetime import datetime
import requests
import re
import json
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

def get_realtime_data_steam(
        name:str = "AK-47 | Bloodsport (Factory New)"
):
    name = get_market_name(name.strip())
    encoded_name = quote(name.encode('utf-8'))
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&market_hash_name={encoded_name}"
    response = requests.get(url, headers=headers, timeout=15)
    time.sleep(1.34)
    data = response.json()
    url = f"https://steamcommunity.com/market/search?appid=730&q={encoded_name}&currency=23"
    response = requests.get(url, headers=headers)
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
        name:str = "Dreams & Nightmares Case"
):
    name = get_market_name(name.strip())
    safe_name = name.replace("|", "-")
    if os.path.exists(f"../data/steam/{safe_name}.csv"):
        df = pd.read_csv(f"../data/steam/{safe_name}.csv")
        return df
    encoded_name = quote(name)
    url = f"https://steamcommunity.com/market/listings/730/{encoded_name}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        time.sleep(0.64)
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
                df.to_csv(safe_name, index=False)
                return df
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return None
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

def init_market_data():
    def crawl_market_hash_names(max_pages=2491):
        data_dir = "../data/steam"
        csv_file = os.path.join(data_dir, "market_hash_name.csv")
        os.makedirs(data_dir, exist_ok=True)
        start = 0
        for page in range(max_pages):
            print(f"开始爬取第 {page + 1} 页数据")
            url = f"https://steamcommunity.com/market/search/render/?query=&start={start}&count=10&search_descriptions=0&sort_column=name&sort_dir=desc&appid=730&norender=1"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data["results"]:
                    break
                count = len(data["results"])
                rows = []
                for item in data["results"]:
                    row={
                        'input_name': item['name'],
                        'market_hash_name': item['hash_name'],
                    }
                    rows.append(row)
                df_new = pd.DataFrame(rows)
                df_new.to_csv(
                    csv_file,
                    mode="a",  # 追加模式
                    header=not os.path.exists(csv_file),  # 仅当文件不存在时写表头
                    index=False,  # 不写入索引
                    encoding="utf-8"
                )
                print(f"已将数据追加到 {csv_file}")
                start += count
                time.sleep(1.92)  # 控制频率，避免被封
            except Exception as e:
                print(f"第 {page + 1} 页爬取失败：{e}")
                break
    return crawl_market_hash_names()

def get_market_name(name:str) -> str:
    # 检测文件中是否已有搜索历史
    def check_market_hash_name(target, csv_path="../data/steam/market_hash_name.csv"):
        if not os.path.exists(csv_path):
            return None
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            return None
        if target in df["market_hash_name"].values:
            return target
        if target in df["input_name"].values:
            target_rows = df[df["input_name"] == target]
            return str(target_rows.iloc[0]["market_hash_name"])
        return None

    if not (check_market_hash_name(name) is None):
        return check_market_hash_name(name)

    # 如果没有，启动模糊搜索（暂时返回一个，未来优化返回列表）
    url = f'https://steamcommunity.com/market/searchsuggestionsresults?appid=730&q={name}'
    def parse_data(data):
        results = data["results"]
        if results:
            first_item = results[0]
            market_hash_name = first_item["market_hash_name"]
            data_dir = "../data/steam"
            csv_file = os.path.join(data_dir, "market_hash_name.csv")
            os.makedirs(data_dir, exist_ok=True)
            new_data = {
                "input_name": [name],
                "market_hash_name": [market_hash_name]
            }
            df_new = pd.DataFrame(new_data)
            df_new.to_csv(
                csv_file,
                mode="a",
                header=not os.path.exists(csv_file),
                index=False,
                encoding="utf-8"
            )
            print(f"已将数据追加到 {csv_file}")
            return market_hash_name
        else:
            print(f"未找到关于{name}的数据")
            return name
    try:
        response = requests.get(url,headers=headers)
        time.sleep(1.64)
        response.raise_for_status()
        data = response.json()
        return parse_data(data)
    except requests.RequestException as e:
        return name

if __name__ == "__main__":
    df = get_realtime_data_steam("梦魇武器箱")
    print(df,"\n")
    df = get_history_data_steam("Dream")
    print(df,"\n")


