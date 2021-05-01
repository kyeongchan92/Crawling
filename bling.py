# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 14:55:13 2021

@author: Admin
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from requests.compat import urlparse, urljoin
from urllib.request import urlopen, Request
import requests
from requests.exceptions import HTTPError
import time
import re
import pandas as pd
#%%
def canfetch(url, agent='*', path='/'):
    robot = RobotFileParser(urljoin(url, '/robots.txt'))
    robot.read()
    return robot.can_fetch(agent, urlparse(url)[2])


def download(url, params={}, headers={}, method='GET', limit=3):
    if canfetch(url) is False:
        print('[Error] ' + url)
#     else:
    try:
        resp = requests.request(method,
                                url,
                                params=params if method == 'GET' else {},
                                data=params if method == 'POST' else {},
                                headers=headers)
        resp.raise_for_status()
    except HTTPError as e:
        if limit > 0 and e.response.status_code >= 500:
            print(limit)
            time.sleep(1)  # => random
            resp = download(url, params, headers, method, limit-1)
        else:
            print('[{}] '.format(e.response.status_code) + url)
            print(e.response.status_code)
            print(e.response.reason)
            print(e.response.headers)
    return resp
#%%
driver = webdriver.Chrome('D:/GoogleDriveSync/16_github_repos/Crawling/chromedriver.exe')
#%%
d = {
     'title': [],
     'subscriberCount': [],
     'category': []
     }
#%%

driver.get('https://vling.net/channel-ranking?sort=subscriberCount')
time.sleep(2)
dom = BeautifulSoup(driver.page_source, 'html.parser')
for box in dom.select('.channel-card-wrap'):
    title = box.select_one('.channel-card-info-title').text.strip()
    subscriberCount = box.select_one('.channel-card-info-status-value').text.strip()

    # 카테고리 따오기
    each_url = 'https://vling.net' + box.select_one('a')['href']
    driver.get(each_url)
    time.sleep(2)
    each_dom = BeautifulSoup(driver.page_source, 'html.parser')
    category = []
    for t in each_dom.select('.channel-detail-category-info-wrap > .channel-detail-category-item-wrap'):
        category.append(t.text)
        print(t.text)
    print(category)
    d['title'].append(title)
    d['subscriberCount'].append(subscriberCount)
    d['category'].append(', '.join(category))
    print(title, subscriberCount, ', '.join(category))
#%%
data = pd.DataFrame(d)
data.to_csv('top100subscriberCount.csv', encoding='utf-8-sig')

vc = data['category'].value_counts()
vc.to_csv('category_vc.csv', encoding='utf-8-sig')





