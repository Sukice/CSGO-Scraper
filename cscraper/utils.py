import os
import time

import pandas as pd
import requests

from cscraper.fetch_steam import headers


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

def init_case_list():
    pass