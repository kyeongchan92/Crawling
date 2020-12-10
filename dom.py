# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 00:36:56 2020

@author: Admin
"""

from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from requests.compat import urlparse, urljoin
from urllib.request import urlopen, Request
import requests
from requests.exceptions import HTTPError
import time
import re
#%%
html = '''
<html>
    <head>
        <title>예제</title>
    <head>
    <body>
        <div>
            <p>
                <a href='/page' class='d' id=asdf>페이지 이동1</a>
                <a>페이지 이동2</a>
            </p>
        </div>
        <footer>
            <a class='d'>페이지 이동3</a>
        </footer>
    </body>
</html>
'''

#%%

# 파싱하기
dom = BeautifulSoup(html, 'html.parser')  # 알아서 역시 수정해줌
dom = BeautifulSoup(html, 'lxml')  # 알아서 수정해줌

print(dom.text)
print(dom.prettify())

dom.html.head.title.text
dom.title.text
dom.body.text, dom.p, dom.a
for _ in list(dom.body.children):
    print(_, type(_))

dom.a.attrs, dom.a['href']

#%% 잘 안됨
for _ in list(dom.body.div.p.children):
    if _.has_attr('class'):
        print(_['class'])

dir(dom.a)
#%%

dom.a['href']

# 문제1. 없는태크(노드) 못거름 => NoneType 객체 => Warning
# 문제2. 특정 노드 => 첫음에 나온 노드 하나만
#%%
dom.find_all('a')[-1].text
dom.find_all('a')[-1]
dom.find('a')['href']
dom.find('a').attrs
len(dom.find_all({'p', 'a'}))
dom.find_all({'p', 'a'})
dom.find_all(['p', 'a'])

dom.find_all('a')
dom.find_all('a', {'id': 'asdf'})

dom.find_all('a', limit=1)  # 딱 하나 찾기
dom.find_all('a', limit=2)

dom.find_all(attrs={'class': 'd'})  # 특정 태그 상관없이 특정 클래스인애들
dom.find_all('a', attrs={'class': 'd'})
#%%
dom.find_all('a')
dom.find_all('a', attrs={'class': 'd'})
dom.footer.find_all('a')
dom.div.find_all('a')

node = dom.footer.a
type(node)
node.attrs
node.find_parent()
node.find_parent().name  # 태그 이름 보고싶으면
for _ in node.find_parents():
    print(_.name)

# 부모는 양쪽에서 받을 수 없으니 recursive 없다
for _ in node.find_parents(limit=2):
    print(_.name)

# 자식, 자손 끝까지
for _ in dom.div.find_all():
    print(_.name)

# 자손은 빼고 자식만
for _ in dom.div.find_all(recursive=False):
    print(_.name)

# 트리 구조에서 어떻게 찾아갈 것인다.
node.find_parent().find_parent().find().find('a').find_next_sibling()


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


resp = download('http://pythonscraping.com/pages/page3.html')
dom = BeautifulSoup(resp.content, 'html.parser')
#%%
node = dom.find('div', {'id': 'footer'})  # 시작할 노드
for _ in node.find_parents():
    print(_.name)
#%% 형제노드로 가서 찾
node.find_parents('div')[0].find_all(recursive=False)[0]['src']
for _ in node.find_previous_siblings():
    print(_.name)
node.find_previous_siblings()[-1]['src']
urljoin(resp.request.url, node.find_previous_siblings()[-1]['src'])
#%% 테이블에서 값 가져오기
node.find_previous_siblings('table')[0].find_all(recursive=False)[3].\
    find('img')['src']
for _ in dom.find('table').find_all(recursive=False)[1:]:
    print(_.find_all('td', recursive=False)[2].text.strip())
#%% attribute로 가져오기
for _ in dom.find_all(attrs={'class': 'gift'}):
    print([td.text.strip() for td in _.find_all()])
#%% '파이썬'검색 결과 제목만 가져오기
url = 'https://www.google.com/search'
params = {
    'q': '',
    'oq': '',
    'aqs': 'chrome.0.69i59l2j69i61l2.826j0j7',
    'sourceid': 'chrome',
    'ie': 'UTF-8'
    }
params['q'] = params['oq'] = '파이썬'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
        537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
resp = download(url, params, headers, 'GET')
dom = BeautifulSoup(resp.content, 'html.parser')
dom.select('h3.')
#%%
for _ in dom.find_all('h3'):
    print(_.text)
#%%
[(_.text.strip(), _.find_parents('a')[0]['href']) for _ in dom.find_all('h3',{'class': 'LC20lb'})]
for _ in dom.find_all('h3', {'class': 'LC20lb'}):
    print(_.find_parents(limit=2)[-1])
    print(_.find_parents()[-1].attrs)
#%%
len(dom.find_all('div', {'class': 'rc'}))
for _ in dom.find_all('div', {'class': 'rc'}):
    print(_.find().find('a')['href'])  # find하면 첫 번째 자식 하나 찾는다
    print(_.find('a').find('h3').text.strip())
#%% 네이버
url = 'https://search.naver.com/search.naver'
params = {
    'sm': 'top_hty',
    'fbm': 0,
    'ie': 'utf8',
    'query': '',
}
params['query'] = '파이썬'
resp = download(url, params, headers, 'GET')
dom = BeautifulSoup(resp.content, 'html.parser')

#%%
for _ in dom.find_all('ul'):
    print(_.find_all('dt'))
    # for a in [dt.find('a') for dt in ]:
    #     print(a['href'], a.text)

#%% 다음
url = 'https://search.daum.net/search'

params = {
    'w': 'tot',
    'DA': 'YZR',
    't__nil_searchbox': 'btn',
    'sug': '',
    'sugo': '',
    'sq': '',
    'o': '',
    'q': ''
}

params['q'] = '파이썬'
resp = download(url, params, headers, 'GET')
dom = BeautifulSoup(resp.content, 'html.parser')

#%%
for _ in dom.find_all('div', {'class': 'wrap_tit'}):
    print(_.find('a')['href'])
    print( _.find('a').text.strip())
    print()

#%% 
url = 'http://example.webscraping.com/places/default/view/Afghanistan-1'
resp = download(url)
dom = BeautifulSoup(resp.content, 'html.parser')
#%%
for _ in dom.select('a'):
    print(_['href'])
#%%
urls = list()
# urls.pop()  # 꺼낼, urls.append()  # 추가
# Queue => 선입선출 FIFO => pop(0)
# Stack => LIFO => pop(-1)
urls.append(url)
seen = list()

while urls:
    seed = urls.pop(0)  # Starting url
    seen.append(seed)  # 재방문 회피
    
    dom = BeautifulSoup(download(seed).text, 'html.parser')  # HTTP
    # for _ in dom.select('a'):  # extract hyperlinks
    #     if _.has_attr('href'):  # 나중에
    #         if _['href'].startswith('/'):  # filter1
    #             newUrls = urljoin(seed, _['href'])  # Normalization
    #             # query부분 (GET방식에서 ? 이후에 나오는 파라미터 생략)
    #             if newUrls not in seen and newUrls not in urls:
    #                 urls.append(newUrls)
    #                 # print(newUrls)
    for _ in [_['href'] for _ in dom.select('a') if _.has_attr('href') and _['href'].startswith('/')]:
        newUrls = urljoin(seed, urlparse(_)[2])
        if newUrls not in seen and newUrls not in urls:
            urls.append(newUrls)
    print(len(urls), len(seen))

# urlparse('http://example.webscraping.com/places/default/user/register?_next=/places/default/view/Turkmenistan-232')

#%%
resp = download('http://pythonscraping.com/pages/page3.html')
dom = BeautifulSoup(resp.text, 'lxml')
#%%
# tag, #id, .class, .class.class.class(3개 클래스가 동시 적용된 애)
# ul.class, ul.class.class.class
# tag, tag, tag => CS
# tag[id=asdf]

dom.select_one('#footer') == dom.select_one('div#footer')
dom.select_one('#footer').text.strip()

# Selector
# tag1, tag2
# tag1 tag2 => 자손 (find_all(recursive=True))
# tag1 > tag2 => 자식 (find_all(recursive=False))
# tag1 + tag2 => 형제(다음노드) => tag2
#%%
dom.select_one('#footer').find_parent().name
len(dom.select('#wrapper > div'))
len(dom.select('#wrapper > *'))
for _ in dom.select('#wrapper > *'):
    print(_.name)
dom.select_one('h1 + div').name
dom.select_one('h1 + div').find_previous_sibling().name
dom.select_one('body > div > h1 + div').name
[_.text.strip() for _ in dom.select('.gift > td:nth-of-type(3)')]
[_['src'] for _ in dom.select('.gift > td > img')]

#%%
url = 'https://www.google.com/search'
params = {
    'q': '',
    'oq': '',
    'aqs': 'chrome.0.69i59l2j69i61l2.826j0j7',
    'sourceid': 'chrome',
    'ie': 'UTF-8'
    }
params['q'] = params['oq'] = '파이썬'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
        537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
resp = download(url, params, headers, 'GET')
dom = BeautifulSoup(resp.content, 'html.parser')
# href를 속성으로 갖는 a, seed가 된다.
urls = [{'url': _['href'], 'depth': 1}
        for _ in dom.select('div.yuRUbf > a[href]')]
len(urls)
#%%
re.findall(r'\b파이썬\b', resp.text)
re.findall(r'\b(\w+)\B파이썬\b', resp.text)
re.findall(r'\b파이썬\B(\w+)\b', resp.text)
# \b파이썬\b
# \b(\w+)\B파이썬\b
# \b파이썬\B(\w+)\b

# 파이썬 파이썬 파이썬 = =3
# ~파이썬 or 파이썬~
# 은, 는, 이, 가~ => 명사
# 강아지를, 강아지가, 강아지는 => Unique
# 강아지+?
#%%
# urls = list()
# urls.pop()  # 꺼낼, urls.append()  # 추가
# Queue => 선입선출 FIFO => pop(0)
# Stack => LIFO => pop(-1)
# urls.append(url)
seen = list()

while urls:
    seed = urls.pop(-1)  # Starting url
    seen.append(seed)  # 재방문 회피
    if seed['depth'] < 4:  # 범위 제한 => Focused Crawling
        dom = BeautifulSoup(download(seed['url']).text, 'html.parser')  # HTTP
        for _ in [_['href'] for _ in dom.select('a[href]') if re.match(r'(?:https?:/)?/\w+(?:[./]\w+)+', _['href'])]:
            newUrls = urljoin(seed['url'], urlparse(_)[2])
            if newUrls not in [_['url'] for _ in seen] and newUrls not in [_['url'] for _ in seen]:
                urls.append({'url': newUrls, 'depth': seed['depth']+1})
        print(len(urls), len())
print(urls)

# temp = '/www.domain.co.kr/service/1/2?key=value/'
# re.match(r'(?:https?:/)?/\w+(?:[./]\w+)+', temp)

# 구글 '파이썬'검색 -> 8개 검색결과(depth=1) -> 다시 링크타고 이동(depth=2) -> depth=3
                                  # 구글(검색어)-Queue pop(0)
#     [1]                       [2]            3   4   5   6   7   8
#     [1-1]  1-2 1-3..     2-1 2-2 2-3...
# 1-1-1 1-1-2...
# => BFS(너비우선탐색)
#                                   구글(검색어)-Stack pop(-1)
#     1   2   3   4   5   6   7   [8]
#                               8-1 8-2 [8-3]
#                                       8-3-1 8-3-2...
# => DFS

#%% 네이버
url = 'https://search.naver.com/search.naver'
params = {
    'sm': 'top_hty',
    'fbm': 0,
    'ie': 'utf8',
    'query': '',
}
params['query'] = '파이썬'
resp = download(url, params, headers, 'GET')
dom = BeautifulSoup(resp.content, 'html.parser')

# href를 속성으로 갖는 a, seed가 된다.
urls = [{'url': _['href'], 'depth': 1}
        for _ in dom.select('ul.lst_total._list_base  a[href]')]
len(urls)
#%%
seen = list()

while urls:
    seed = urls.pop(-1)  # Starting url
    seen.append(seed)  # 재방문 회피
    # if seed['depth'] < 4:  # 도메인 제한 => Focused Crawling
    dom = BeautifulSoup(download(seed['url']).text, 'html.parser')  # HTTP
    print(dom)
    for _ in [_['href'] if _.has_attr('href') else _['src'] for _ in dom.select('a[href], #mainFrame') if re.match(r'(?:https?:/)?/\w+(?:[./]\w+)+', _['href'] if _.has_attr('href') else _['src'])]:
        newUrls = urljoin(seed['url'], _)
        if newUrls not in [_['url'] for _ in seen] and newUrls not in [_['url'] for _ in seen]:
            urls.append({'url': newUrls, 'depth': seed['depth']+1})
    print(len(urls), len(seen))
    break    

newUrls


#%% 로그인하기
driver = webdriver.Chrome('chromedriver/chromedriver.exe')
driver.get('https://www.jobplanet.co.kr/welcome/index')
# dir(driver.find_element_by_class_name('link_login'))

driver.find_element_by_class_name('link_login').click()
#%%
with open('account.json') as f:
    account = json.load(f)
#%%
# . => 현재위치
# / => root
# / => 자식
# // => 자손
# [@class='속성']
#%%
driver.find_element_by_xpath('//input[@id="id"]').tag_name
driver.find_element_by_xpath('//span/input').get_attribute('placeholder')

dom = BeautifulSoup(driver.page_source, 'html.parser')
dom.select_one('#id').find_parent().find_parent().find_parent().find_parent() #비밀번호 태그 위치 찾기
#%% id, pw 넣기
driver.find_element_by_css_selector('#id').clear() #id clear하기
driver.find_element_by_css_selector('#id').send_keys(account['id']) #id 넣기
driver.find_element_by_id('pw').clear() #pw clear하기
driver.find_element_by_id('pw').send_keys(account['password']) #pw 넣기
#%% 로그인버튼 클릭
driver.find_element_by_css_selector('input[type=submit][id]').get_attribute('id') # [id] : id라는 속성을 가진 태그
driver.find_element_by_css_selector('input[type=submit][id]').click()









































































































