
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
    'Accept-Language': 'en-US,en;q=0.9',
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
    url = f"https://steamcommunity.com/market/search?appid=730&q={encoded_name}"
    response = requests.get(url, headers=headers)
    time.sleep(1.24)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        listing_number = soup.find('span', class_='market_listing_num_listings_qty')['data-qty']
        normal_price_text = soup.find('span', class_='normal_price', attrs={'data-price': True}).get_text(strip=True)
        print(f"在售数量：{listing_number}")
        print(f"正常价格：{normal_price_text}")
    else:
        print(f"请求失败，状态码：{response.status_code}")

    def parse_data(data):
        print(data)
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
    if os.path.exists(f"./data/steam/{name}.csv"):
        df = pd.read_csv(f"./data/steam/{name}.csv")
        return df
    encoded_name = quote(name.encode('utf-8'))
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
                df = df[['date', 'price', 'volume']]
                if not os.path.exists(f"./data/steam"):
                    os.makedirs("./data/steam", exist_ok=True)
                filename = f"./data/steam/{name}.csv"
                df.to_csv(filename, index=False)
                return df
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return None
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def init_market_data():
    #本地测试中
    def crawl_market_hash_names(appid, max_pages=100):
        market_hash_names = []
        start = 0
        count = 100  # 每页100条
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        for page in range(max_pages):
            url = f"https://steamcommunity.com/market/search/render/?appid={appid}&start={start}&count={count}&norender=1"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data["results"]:
                    break  # 无更多数据，退出循环

                # 提取当前页的 market_hash_name
                for item in data["results"]:
                    market_hash_names.append(item["hash_name"])

                print(f"已爬取第 {page + 1} 页，累计 {len(market_hash_names)} 个物品")
                start += count
                time.sleep(2)  # 控制频率，避免被封

            except Exception as e:
                print(f"第 {page + 1} 页爬取失败：{e}")
                break

        market_hash_names = list(set(market_hash_names))
        return market_hash_names

    appid = 730
    hash_names = crawl_market_hash_names(appid, max_pages=100)

    with open("cs2_market_hash_names_crawled.txt", "w", encoding="utf-8") as f:
        for name in hash_names:
            f.write(name + "\n")

    print(f"最终获取 {len(hash_names)} 个 unique market_hash_name")

def get_market_name(name:str) -> str:
    def check_market_hash_name(target, csv_path="./data/steam/market_hash_name.csv"):
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

    if check_market_hash_name(name) is not None:
        return check_market_hash_name(name)
    encoded_name = quote(name)
    url = f'https://steamcommunity.com/market/searchsuggestionsresults?q={encoded_name}'
    print(url)
    def parse_data(data):
        print(data)
        results = data["results"]
        if results:
            first_item = results[0]
            market_hash_name = first_item["market_hash_name"]
            data_dir = "./data/steam"
            csv_file = os.path.join(data_dir, "market_hash_name.csv")
            os.makedirs(data_dir, exist_ok=True)
            new_data = {
                "input_name": [name],  # 注意：pandas 需要列表格式
                "market_hash_name": [market_hash_name]
            }
            df_new = pd.DataFrame(new_data)
            df_new.to_csv(
                csv_file,
                mode="a",  # 追加模式
                header=not os.path.exists(csv_file),  # 仅当文件不存在时写表头
                index=False,  # 不写入索引
                encoding="utf-8"
            )
            print(f"已将数据追加到 {csv_file}")
            return market_hash_name
        else:
            print(f"未找到关于{name}的数据")
            return None
    try:
        response = requests.get(url, headers=headers, timeout=15)
        time.sleep(0.64)
        response.raise_for_status()
        data = response.json()
        return parse_data(data)
    except requests.RequestException as e:
        return name




if __name__ == "__main__":
    print(get_realtime_data_steam())

