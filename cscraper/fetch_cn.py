import datetime
import time
import json

import pandas as pd
import requests
from cscraper.utils import get_random_headers
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
                        lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%Y%m%d')
                    )

                    df['name'] = item['marketHashName']
                    df = df[['name','date', 'price']]
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
    return get_data_csdt(name, mode = 'history')

def get_history_data_csdt(name = "梦魇武器箱"):
    return get_data_csdt(name, mode = 'realtime')



if __name__ == '__main__':
    print(get_realtime_data_csdt(name = "梦魇武器箱"))
    print(get_history_data_csdt(name = "梦魇武器箱"))