# coding: utf-8
import requests
import urllib
from lxml import html
from urllib import urlopen

import nltk
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urlparse import urlsplit
from collections import deque
import re




def getAllLinks(url):
    href = []
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        href = tree.xpath('//a/@href')
    except:
        pass
    return list(set(href))

def getMailTabFromWebsite(url):
    adressMailList = []
    return crawlWebPage(url)
    try:

        newContactWebsite = requests.get(url)
        contactWebsiteTree = html.fromstring(newContactWebsite.content)

        getMailTab = contactWebsiteTree.xpath('//*[contains(text(),"@")]/text()')
        print getMailTab
        for text in getMailTab:
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            for email in emails:

                if email.endswith('.com') or email.endswith('.fr') or email.endswith('.net'):
                    print email
                    adressMailList.append(email)
    except:
        pass
    return list(set(adressMailList +url))

def crawlWebPage(url):
    # a queue of urls to be crawled
    try:
        new_emails = []
        # extract base url to resolve relative links
        parts = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        response = requests.get(url)
        new_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I)

    except:
        # ignore pages with errors
        pass
    return new_emails
