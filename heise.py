#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from IPython.core.display import display,HTML
import re
import sys
import os
import time

def showTimeElapsed(clock):
    if clock:
        elapsed = clock.elapsed()
        msg = "Time elapsed: %s" % fmtTime(elapsed)
        print(msg)

class Stopwatch():
    def __init__(self):
        self.starttime = time.time()
    def elapsed(self,reset=False):
        t = time.time() - self.starttime
        if reset:
            self.reset()
        return t
    def reset(self):
        self.starttime = time.time()

def fmtTime(t):
    str = "%4.2f seconds" % t
    if t > 60:
        str = "%4.2f minutes " % (t/60)
    if t > 3600:
        str = "%4.2f hours   " % (t/3600)
    return str

# In[2]:


css = """
<style>
.metadata {
  background-color: RGB(222, 224, 227);
}
.posting {
  border-style: solid;
  border-radius: 5px;
  padding: 2px;
  border-left-style: solid;
  border-left-width: 3px;
  border-width: 1px;
}
.forum-blockquote {
  border-left-style: solid;
  border-left-width: 3px;
  color: grey;
  padding-left: 5px;
}
</style>
"""


# In[3]:


def getId(url):
    m = re.search("posting-(\\d*)", url)
    if m:
        return m.group(1)
    else:
        return ""

class Posting():
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.status_code = 0
        self.content = ""
        self.user = ""
        self.user_info = ""
        self.timestamp = ""
        self.parent = None
        self.parent_url = ""
        self.thread_url = ""
        self.id = getId(url)
        self.rating = 0
    def getContent(self):
        r = requests.get(self.url)
        self.status_code = r.status_code
        soup = BeautifulSoup(r.text, "html.parser")
        for div in soup.find_all('div',{"class": "post"}):
            self.content = str(div)
        self.getUser(soup)
        self.getTime(soup)
        self.getThread(soup)
        self.getRating(soup)
    def getUser(self,soup):
        for div in soup.find_all('div',{"class": "userbar"}):
            for span in div.find_all('span'):
                if span.get('class') and 'pseudonym' in span.get('class'):
                    self.user = span.text.strip()
            for p in div.find_all('p'):
                    self.user_info = p.text.strip()
    def getTime(self,soup):
        for time in soup.find_all('time'):
            self.timestamp = time.text
    def getThread(self,soup):
        for li in soup.find_all('li',{"class": "posting"}):
            for a in li.find_all('a'):
                if a.text.strip() == "Threads":
                    self.thread_url = a.get("href")
    def getRating(self,soup):
        for img in soup.find_all('img',{"class": "posting_rating_chart"}):
            self.rating = img.get('alt')
    def render(self, lvl, cnt=0):
        def renderRating(rating):
            if int(rating) == 0:
                return ""
            html = f"<span style=\"float: right\">"
            if int(rating) < 0:
                html += f"<meter style=\"margin-right: 5px\" low=\".98\" optimum=\".99\" high=\".98\" value=\"{int(self.rating)/-100.0}\"></meter>"
            html += f"Rating: {self.rating}"
            if int(rating) > 0:
                html += f"<meter style=\"margin-left: 5px\" value=\"{int(self.rating)/100.0}\"/></meter>"
            return html+"</span>"

        pxels = 20*lvl
        indent = " "*lvl
        counter = ""
        if cnt:
            counter = f"<span style=\"float: right\">{cnt}</span>"
        html = f"<div style=\"margin-left: {pxels};\"class=\"posting\">{counter}<a target=\"_NEW_\" href=\"{self.url}\"><h2>{self.title}</h2></a>"
        html += f"<div class=\"metadata\">{renderRating(self.rating)}{self.user}<br/>{self.user_info}<br/>{self.timestamp}</div>"
        html += self.content + "</div>"
        print(("[%4d]\t" % cnt)+indent+self.title)
        cnt += 1
        return html, cnt

        pxels = 20*lvl
        html = f"<div style=\"margin-left: {pxels};\"class=\"posting\"><a target=\"_NEW_\" href=\"{self.url}\"><h27>{self.title}</h2></a>"
        html += f"<div class=\"metadata\">{renderRating(self.rating)}{self.user}<br/>{self.user_info}<br/>{self.timestamp}</div>"
        html += self.content + "</div>"
        return html


def retrieveThread(txt,html,ids,lvl=0,cnt=1):
    soup = BeautifulSoup(txt, "html.parser")
    for li in soup.find_all('li',{"class": "posting_element"}):
        a = li.find('a',{"class": "posting_subject"})
        if not a:
            continue
        url = a.get('href')
        p = Posting(a.text.strip(),url)
        if p.id in ids:
            continue
        ids.add(p.id)
        p.getContent()
        if 'no_subthread' not in li.get('class'):
            if not len(li.find_all('ol')) and (lvl > 0):
                h, cnt = p.render(lvl,cnt)
                html += h
            else:
                for ol in li.find_all('ol',{"class": "tree_sub_thread"})[:1]:
                    h, cnt = p.render(lvl,cnt)
                    html += h
                    html, cnt = retrieveThread(str(ol),html,ids,lvl=lvl+1,cnt=cnt)
        else:
            h, cnt = p.render(lvl,cnt)
            html += h
    return html, cnt

def numberEntries(txt):
    soup = BeautifulSoup(txt, "html.parser")
    elements = soup.find_all('li',{"class": "posting_element"})
    return len(elements)

try:
    argv = sys.argv[1]
except IndexError:
    print("Please specify a URL to a heise.de discussion thread !")
    sys.exit(1)
if "Kommentare" not in sys.argv[1]:
    print("Please specify a URL to a heise.de discussion thread !")
    sys.exit(1)        
# In[29]:

# Retrieve thread and all postings
clock = Stopwatch()
page = 0
cnt = 1
html = ""
while True:
    page += 1
    argv1 = argv
    if page > 1:
        argv1 = argv.replace("comment",f"page-{page}")
    session = requests.Session()
    r = session.get(argv1)
    if not numberEntries(r.text):
        break
    soup = BeautifulSoup(r.text, "html.parser")
    # Get first posting
    if page == 1:
        for a in soup.find_all('a',{"class": "forum_edit_links"}):
            title = a.text
            article_url = a.get('href')
            print(f"Retrieving comments for article \"{title}\" ...")
            html = f"<html><head>{css}<title>{title}</title></head><body><a target=\"_NEW_\" href=\"{article_url}\"><h1>{title}</h1></a>"
            break
    for a in soup.find_all('a',{"class": "posting_subject"}):
        url = a.get('href')
        break
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    url = ""
    for li in soup.find_all('li',{"class": "posting"}):
        try:
            url = li.find('a').get('href')
        except AttributeError: pass
        if url:
            break
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all('a',{"class": "thread_expand_all"}):
        url = a.get('href')
        break
    r = session.get(url)
    with open('heise.xml','w',encoding='utf8') as f:
        f.write(r.text)
    # Retrieve thread and all postings
    html, cnt = retrieveThread(r.text,html,set(),cnt=cnt)
html += "</body></html>"
print(f"\n{cnt} postings retrieved.")

fn = fn = 'heise.html'
with open(fn,'w',encoding='utf8') as f:
    f.write(html)



os.system(fn)
showTimeElapsed(clock)
