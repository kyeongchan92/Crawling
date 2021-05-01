# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 19:13:59 2021

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
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from konlpy.tag import Kkma,Hannanum, Komoran, Mecab, Okt
from collections import Counter
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
def scroll_down(last_page_height):
    endpoint = 0
    divide = 1000
    move_distance = last_page_height/divide
    while endpoint < last_page_height:
        driver.execute_script(f"window.scrollTo(0, {endpoint})")
        # time.sleep(0.5)
        endpoint += move_distance
#%%
def convert_to_view(s):
    p = re.compile(r'([\d\,]+)')
    view_str = re.search(p, s)[0]
    view_str_rep = view_str.replace(',', '')
    
    return int(view_str_rep)
#%%
def convert_to_sec(s):
# '실시간'.split(':')
# '12:32'.split(':')
# '1:12:32'.split(':')
    split_list = s.split(':')
    if len(split_list) == 1:
        return '실시간'
    elif len(split_list) == 2:
        return int(split_list[0]) * 60 + int(split_list[1])
    elif len(split_list) == 3:
        return int(split_list[0]) * 3600 + int(split_list[1]) * 60 +\
            int(split_list[2])
    else:
        return '???????????????????????'
#%%
def convert_to_date(s):
    if s == '':
        return ''
    p2 = re.compile(r'([\d]+)([분시간일주]*)')
    
    ALL = re.search(p2, s)[0]
    number = re.search(p2, s)[1]
    timescope = re.search(p2, s)[2]
    
    now = datetime.datetime.now()
    print(f'date:{s}, 단위:{timescope}, number:{number}')
    if timescope == '분':
        return now + timedelta(minutes=-int(number))
    elif timescope =='시간':
        return now + timedelta(hours=-int(number))
    elif timescope == '일':
        return now + timedelta(days=-int(number))
    elif timescope == '주':
        return now + timedelta(weeks=-int(number))
    else:
        return '?????????????'
    
#%%
def convert_to_n_subs(s):
    p = re.compile(r'([\d\.]+)([천만]?)')
    ALL = re.search(p, s)[0]
    number = re.search(p, s)[1]
    Kor10K = re.search(p, s)[2]
    
    if Kor10K == '천':
        return int(float(number) * 1000)
    elif Kor10K == '만':
        return int(float(number) * 10000)
    else:
        return int(float(number))
#%%
def convert_to_upload_date(s):
    p = re.compile(r'(\d+)')
    findall = re.findall(p, s)
    if len(findall) == 3:
        year, month, day = int(findall[0]), int(findall[1]), int(findall[2])
        return datetime.date(year, month, day)
    else:
        return '스트리밍방송중'
    
#%%
def convert_thumb_to_num(s):
    p = re.compile(r'([\d\.]+)([천만]?)')
    ALL = re.search(p, s)[0]
    number = re.search(p, s)[1]
    Kor10K = re.search(p, s)[2]
    
    if Kor10K == '천':
        return int(float(number) * 1000)
    elif Kor10K == '만':
        return int(float(number) * 10000)
    else:
        return int(float(number))
    
#%%
def convert_to_reply(s):
    p = re.compile(r'([\d\,]+)')
    reply_str = re.search(p, s)[0]
    reply_str_rep = reply_str.replace(',', '')
    
    return int(reply_str_rep)
#%% 창띄우기

driver = webdriver.Chrome('D:/GoogleDriveSync/16_github_repos/Crawling/chromedriver.exe')
#%%
# 이동
driver.get('https://www.youtube.com/user/ytnnews24/videos')  # YTN
driver.get('https://www.youtube.com/user/JTBC10news/videos')  # JTBC
driver.get('https://www.youtube.com/sbs8news/videos')  # SBS
driver.get('https://www.youtube.com/c/newskbs/videos')  # kbs
driver.get('https://www.youtube.com/c/tvchanews/videos')  # 채널A
driver.get('https://www.youtube.com/c/MBCNEWS11/videos')  # MBC
time.sleep(10)

#%%
SCROLL_PAUSE_SEC = 2
n_of_box = 0
# '1일 전' '1주 전'
date_raw = ''
to_this_date = '2일 전'
while date_raw != to_this_date:
    
    # 스크롤 끝까지 아래로 내리기
    last_page_height = driver.execute_script("return document.documentElement.\
                                             scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {last_page_height})")
    time.sleep(SCROLL_PAUSE_SEC)
    
    #내린 상태에서 dom가져오기
    dom = BeautifulSoup(driver.page_source, 'html.parser')
    n_of_box = len(dom.select('ytd-grid-video-renderer.style-scope'))

    #영상(box) 몇 개인지 확인하기
    box = dom.select('ytd-grid-video-renderer.style-scope')[-1]
    date_raw = box.select_one(
        'span.style-scope.ytd-grid-video-renderer + span').text.strip()
    print(n_of_box, date_raw)

last_page_height = driver.execute_script("return document.documentElement.\
                                             scrollHeight")
scroll_down(last_page_height)
time.sleep(SCROLL_PAUSE_SEC)
#%% 검사
dom = BeautifulSoup(driver.page_source, 'html.parser')
fail_idx = []
for i, box in enumerate(dom.select('ytd-grid-video-renderer.style-scope')):
    try:
        img = box.select_one('img')['src']
    except KeyError:
        fail_idx.append(i)
print(len(fail_idx))
#%%
n_of_box = fail_idx[0] - 1
#%% video tab
d_videotab = {
     'channel': [], 'n_subs': [], 'title': [],'thumbnail': [],
     'length_raw': [], 'length': [], 'url': []
     }

dom = BeautifulSoup(driver.page_source, 'html.parser')
channel = dom.select_one('yt-formatted-string.style-scope.ytd-channel-name').\
    text.strip()
n_subs_raw = dom.select_one(
    'yt-formatted-string.style-scope.ytd-c4-tabbed-header-renderer'
    ).text.strip()
n_subs = convert_to_n_subs(n_subs_raw)
for i, box in enumerate(dom.select('ytd-grid-video-renderer.style-scope')):
    
    title = box.select_one('#video-title').text.strip()
    thumbnail = box.select_one('img')['src']
    length_raw = box.select_one('span').text.strip()
    length = convert_to_sec(length_raw)
    url = 'https://www.youtube.com' + box.select_one('a#thumbnail')['href']
    
    # 어펜드
    d_videotab['channel'].append(channel)
    d_videotab['n_subs'].append(n_subs)
    d_videotab['title'].append(title)
    d_videotab['thumbnail'].append(thumbnail)
    d_videotab['length_raw'].append(length_raw)
    d_videotab['length'].append(length)
    d_videotab['url'].append(url)
    
    print(f'{i}/{n_of_box-1}')
    
    if len(d_videotab['channel']) != len(d_videotab['thumbnail']):
        print('beep!!')
        print(title)
        break
    
    if i  == n_of_box - 1:
        break

data_videotab = pd.DataFrame(d_videotab)
#%% play page

d_playpage = {
    'upload_date_raw': [], 'upload_date': [],
    'view_raw': [], 'view': [],
    'like_raw': [], 'like': [],
    'dislike_raw': [], 'dislike': [],
    'reply_raw': [], 'reply': [],
    'coll_date': []
    }

n_url = len(d_videotab['url'])

for i, url in enumerate(d_videotab['url']):
    # 재생 페이지 이동
    driver.get(url)
    time.sleep(6)
    
    # 스크롤 내리기 (댓글 수가 안뽑힐때가 있음)
    last_page_height = driver.execute_script("return document.documentElement.\
                                             scrollHeight")
    scroll_down(last_page_height)
    time.sleep(3)
    # dom 가져오기
    dom = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 파싱
    upload_date_raw = dom.select_one(
        'div#date \
            yt-formatted-string.style-scope.ytd-video-primary-info-renderer'
            ).text.strip()
    upload_date = convert_to_upload_date(upload_date_raw)
    view_raw = dom.select_one(
        'span.view-count.style-scope.yt-view-count-renderer').text
    view = convert_to_view(view_raw)
    like_raw = dom.select_one('#menu-container yt-formatted-string').text
    like = convert_thumb_to_num(like_raw)
    dislike_raw = dom.select_one(
        '#menu-container yt-formatted-string:nth-of-type(2)').text
    dislike = convert_thumb_to_num(dislike_raw)
    try:
        reply_raw = dom.select_one('h2#count').text.strip()
    except AttributeError:
        reply = '스트리밍방송중'
    else:
        reply = convert_to_reply(reply_raw)
    coll_date = datetime.date.today()
    
    d_playpage['upload_date_raw'].append(upload_date_raw)
    d_playpage['upload_date'].append(upload_date)
    
    d_playpage['view_raw'].append(view_raw)
    d_playpage['view'].append(view)
    
    d_playpage['like_raw'].append(like_raw)
    d_playpage['like'].append(like)
    
    d_playpage['dislike_raw'].append(dislike_raw)
    d_playpage['dislike'].append(dislike)
    
    d_playpage['reply_raw'].append(reply_raw)
    d_playpage['reply'].append(reply)
    
    d_playpage['coll_date'].append(coll_date)
    
    print(d_videotab['title'][i])
    print(f'{i}/{n_url}, {upload_date}, {view}, {like}, {dislike}, {reply}')
    print('---------------------')

data_playpage = pd.DataFrame(d_playpage)
#%%
data = pd.read_csv('')
#%%
view = data['view']
#%%
len(dom.select('ytd-grid-video-renderer.style-scope'))

dir(dom)

print(box.prettify)
box.select('img')

last_height = driver.execute_script("return document.body.scrollHeight")


#%%
p = re.compile(r'([\d\.]+)([천만]?)')
re.search(p, '902회')[0]
re.search(p, '902회')[1]
re.search(p, '902회')[2]

re.search(p, '1.3천회')[0]
re.search(p, '1.3천회')[1]
re.search(p, '1.3천회')[2]

re.search(p, '1.6만회')[0]
re.search(p, '1.6만회')[1]
re.search(p, '1.6만회')[2]

        
#%%
	view
310	조회수 1.3천회
311	조회수 5.2천회
312	조회수 1.6만회
313	조회수 902회
314	조회수 1.2천회
315	조회수 2.8천회
#%%
for _ in view:
    print(_, convert_to_int(_))
#%%
date = data.date
#%%

p2 = re.compile(r'([\d]+)([분시간일주]*)')
re.search(p2, '30분 전')[0]
re.search(p2, '30분 전')[1]
re.search(p2, '30분 전')[2]

re.search(p2, '5시간 전')[0]
re.search(p2, '5시간 전')[1]
re.search(p2, '5시간 전')[2]

re.search(p2, '1일 전')[0]
re.search(p2, '1일 전')[1]
re.search(p2, '1일 전')[2]

#%%
print('현재 시간부터 5일 뒤')
print(time2 + timedelta(days=5)) # 2018-07-28 20:58:59.666626
print('현재 시간부터 3일 전')
print(time2 + timedelta(days=-3)) # 2018-07-20 20:58:59.666626
print('현재 시간부터 1일 뒤의 2시간 전')
print(time2 + timedelta(days=1, hours=-2))
#%%
10년째 공사 중 춘천
#%%
for _ in date:
    print(_, convert_to_date(_))
#%%

	date
7	30분 전
8	33분 전
9	34분 전
10	35분 전

	date
68	5시간 전
69	5시간 전
70	6시간 전
71	6시간 전
72	6시간 전
73	6시간 전
74	스트리밍 시간: 6시간 전
75	6시간 전
76	6시간 전
	date
181	23시간 전
182	23시간 전
183	1일 전
184	1일 전
#%%
data.groupby('date').mean('view')
#%%
date_to_day = []


for _ in data['date']:
    print(_.year)
a = data['date'][0]

a.date


datetime.datetime.today().day
#%%
%matplotlib inline
# plt.figure(figsize=(10,8))
plt.rc('font', family='NanumGothic') # For Windows
plt.scatter(data.index, d['view'])
plt.xticks(rotation=45)
plt.title('YTN news view count')
plt.xlabel('Index')
#%%
kkma = Kkma()
hannanum = Hannanum()
komoran = Komoran()
okt = Okt()
#%%
a = data[data['view'] > (1 * 1e4)]
#%%
b = hannanum.nouns('\n'.join(a['title']))
#%%
count = Counter(b)
#%%
noun_list = count.most_common(15)

#%%
#%%
A = data[data['view'] <= (1 * 1e4)]
#%%
B = hannanum.nouns('\n'.join(A['title']))
#%%
count = Counter(B)
#%%
NOUN_list = count.most_common(15)
#%%
a['length'].mean()
A['length'].mean()
#%%
z = a['length']
plt.scatter(a['length'].reset_index()['length'], a['view'], c='b')
plt.xlabel('Length(Sec)')
plt.ylabel('View')
plt.xlim(0, 16500)
plt.ylim(10000, 1100000)
#%%
plt.scatter(A['length'], A['view'])
plt.xlabel('Length(Sec)')
plt.ylabel('View')
plt.xlim(0, 16500)
plt.ylim(0, 10000)
#%%
plt.scatter( data['view'], data['length'])
plt.ylabel('Length(Sec)')
plt.xlabel('View')
#%%
driver.close()













