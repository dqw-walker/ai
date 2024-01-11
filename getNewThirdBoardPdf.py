import requests
import time
import random
import json
import pandas as pd

# 定义一个列表，存储常见的用户代理头，随机选择其中一个来模拟浏览器请求
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/100.0.1000.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/14.1.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/99.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/99.0.9999.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/13.1.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.9876.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/98.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/98.0.9876.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/12.1.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.8765.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/97.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/97.0.8765.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/11.1.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.7654.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/96.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/96.0.7654.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/10.1.2",
]



# 使用Session对象来维持会话状态和Cookies
session = requests.Session()

def req(stock, year, org_dict):
    # 随机选择用户代理头
    user_agent = random.choice(user_agents)

    # post请求地址
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        "pageNum": "1",
        "pageSize": "30",
        "tabName": "fulltext",
        "stock": stock + "," + org_dict[stock],
        "seDate": f"{str(int(year) + 1)}-01-01~{str(int(year) + 1)}-12-31",
        "column": "third",
        "category": "category_dqgg",
        "isHLtitle": "true",
        "sortName": "time",
        "plate": "neeq",
        "sortType": "desc"
    }

    headers = {
        "User-Agent": user_agent,  # 设置随机选择的用户代理头
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # 使用Session发送请求
        req = requests.post(url, data=data, headers=headers)

        if json.loads(req.text)["announcements"]:
            for item in json.loads(req.text)["announcements"]:
                if "摘要" not in item["announcementTitle"] and "英文" not in item["announcementTitle"] and "半年度" not in item["announcementTitle"]:
                    if "年年度报告" in item["announcementTitle"]:
                        adjunctUrl = item["adjunctUrl"]  # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
                    pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
                    r = requests.get(pdfurl)
                    #再加上item.secName，可以将股票名称也加入文件名中
                    f = open("年报" + "/" + stock + "-" +item["secName"]+"-"+ year + "年度报告" + ".pdf", "wb")
                    f.write(r.content)
                    print(f"{stock}-{year}年报下载完成！")  # 打印进度
                    break
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")

        # 该函数主要是通过http://www.cninfo.com.cn/new/data/szse_stock.json该json数据，找到每个stock对应的orgid，并存储在字典org_dict中
def get_orgid():
    org_dict = {}
    #org_json = requests.get("http://www.cninfo.com.cn/new/data/szse_stock.json").json()["stockList"]
    org_json = requests.get("http://www.cninfo.com.cn/new/data/gfzr_stock.json").json()["stockList"]

    for i in range(len(org_json)):
        org_dict[org_json[i]["code"]] = org_json[i]["orgId"]

    return org_dict

if __name__ == "__main__":
    pdlist = pd.read_excel("stockcode.xlsx", converters={'stockcode': str})["stockcode"]
    stock_list = pdlist.to_numpy().tolist()

    org_dict = get_orgid()

    for stock in stock_list:
        for year in ["2022"]:
            req(stock, year, org_dict)
            time.sleep(random.randint(0, 2))
