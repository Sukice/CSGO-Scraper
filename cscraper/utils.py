import csv
import json
import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def crawl_search_list(file_path, max_pages=10, require=""):
    start = 0
    for page in range(max_pages):
        print(f"开始爬取第 {page + 1} 页/ {max_pages} 页数据")
        url = f"https://steamcommunity.com/market/search/render/?query=&start={start}&count=10&search_descriptions=0&sort_column=name&sort_dir=desc&appid=730&norender=1"+require
        try:

            response = requests.get(url, headers=get_random_headers())
            response.raise_for_status()
            data = response.json()
            print(data)
            if not data["results"]:
                break
            count = len(data["results"])
            rows = []
            for item in data["results"]:
                row = {
                    'input_name': item["asset_description"]['name'],
                    'market_hash_name': item["asset_description"]['market_hash_name'],
                    'type': item["asset_description"]['type'],
                }
                rows.append(row)
            df_new = pd.DataFrame(rows)
            df_new.to_csv(
                file_path,
                mode="a",  # 追加模式
                header=not os.path.exists(file_path),  # 仅当文件不存在时写表头
                index=False,  # 不写入索引
                encoding="utf-8",
                quoting=csv.QUOTE_NONNUMERIC
            )
            print(f"已将数据追加到 {file_path}")
            start += count
            time.sleep(5)  # 控制频率，避免被封
        except Exception as e:
            print(f"第 {page + 1} 页爬取失败：{e}")
            break


def init_database_namedata_all():
    data_dir = "./database/namedata"
    csv_file = os.path.join(data_dir, "all_name_list.csv")
    os.makedirs(data_dir, exist_ok=True)
    return crawl_search_list(csv_file, 2492)

def init_database_namedata_case():
    print("开始初始化箱子列表，请勿中途退出")
    data_dir = "./database/namedata"
    csv_file = os.path.join(data_dir, "case_name_list.csv")
    os.makedirs(data_dir, exist_ok=True)
    require = "&category_730_Type%5B%5D=tag_CSGO_Type_WeaponCase"
    return crawl_search_list(csv_file, 44, require)


import random
def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ]
    accepts = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "application/json, text/plain, */*",
        "text/plain, text/html, application/xhtml+xml",
        "image/webp,image/apng,image/*,*/*;q=0.8",
        "application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
    ]
    accept_languages = [
        "zh-CN,zh;q=0.9",
    ]
    accept_encodings = [
        "gzip, deflate, br",
        "gzip, deflate",
        "br, gzip",
        "deflate, br"
    ]
    connections = ["keep-alive", "close"]
    cache_controls = ["max-age=0", "no-cache", "max-age=3600", "no-store"]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": random.choice(accepts),
        "Accept-Language": random.choice(accept_languages),
        "Accept-Encoding": random.choice(accept_encodings),
        "Connection": random.choice(connections),
        "Cache-Control": random.choice(cache_controls)
    }
    return headers
color_to_rarity = {
    '4b69ff': '消费级',  # 蓝色 - 普通
    '8847ff': '工业级',  # 紫色 - 工业级
    'd32ce6': '保密',  # 粉色 - 军规级
    'eb4b4b': '受限',  # 红色 - 受限
    'ffd700': '隐秘'  # 金色 - 隐秘
}
def init_database_casecontent():
    if not os.path.exists("./database/namedata/case_name_list.csv"):
        init_database_namedata_case()
        time.sleep(5)
    df = pd.read_csv("./database/namedata/case_name_list.csv",
                     sep=",",
                     quoting=csv.QUOTE_NONNUMERIC,
    )
    for case_name in df['market_hash_name']:
        if not os.path.exists(f"./database/casedata/case_content/{case_name}.csv"):
            os.makedirs(f"./database/casedata/case_content/", exist_ok=True)
        else:
            continue
        url = "https://steamcommunity.com/market/listings/730/"+case_name
        response = requests.get(url, headers=get_random_headers())
        time.sleep(5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    if 'g_rgAssets' in script.string:
                        match = re.search(r'var g_rgAssets = ({.*?});', script.string, re.DOTALL)
                        if match:
                            assets_json = match.group(1)
                            assets_data = json.loads(assets_json)
                            items = []
                            try:
                                item_data = assets_data['730']['2'][list(assets_data['730']['2'].keys())[0]]
                                descriptions = item_data['descriptions']
                                for desc in descriptions:
                                    value = desc.get('value', '').strip()
                                    color = desc.get('color', '')
                                    name = desc.get('name', '').strip()
                                    if value and name == "attribute" and color:
                                        rarity = color_to_rarity.get(color, 'Unknown')
                                        items.append({
                                            'name': value,
                                            'rarity': rarity
                                        })
                                df = pd.DataFrame(items)
                                df.to_csv(f"./database/casedata/case_content/{case_name}.csv",
                                            index=False,
                                            quoting = csv.QUOTE_NONNUMERIC,
                                )
                            except KeyError as e:
                                print(f"数据结构错误: {e}")
                                print(url)

if __name__ == "__main__":
    init_database_namedata_all()