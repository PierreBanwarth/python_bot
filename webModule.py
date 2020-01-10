# coding: utf-8
import requests
import urllib3
from lxml import html

import nltk
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from collections import deque
import re
from validate_email import validate_email




def getAllLinks(url):
    href = []
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        href = tree.xpath('//a/@href')
    except:
        pass
    return list(set(href))

def searchForMailInWebsite(url):
    finalResult = []
    for item in getAllLinks(url):
        if url in item:
            finalResult += getMailTabFromWebsite(item)
    return finalResult

def getMailTabFromWebsite(url):
    finalMailing = []
    # a queue of urls to be crawled
    if not 'mailto' in url:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36','Upgrade-Insecure-Requests': '1', 'x-runtime': '148ms'},
            allow_redirects=True
        ).content
        soup = BeautifulSoup(response, "html.parser")
        email = soup(text=re.compile(r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*'))
        _emailtokens = str(email).replace("\\t", "").replace("\\n", "").split(' ')
        if len(_emailtokens):
            results = [match.group(0) for token in _emailtokens for match in [re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(token.strip()))] if match]
            for item in results:
                if validate_email(item):
                    if item.endswith('.com') or item.endswith('.org') or item.endswith('.eu') or item.endswith('.bzh') or item.endswith('.fr'):
                        finalMailing.append(item)
    return finalMailing
