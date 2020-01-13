# coding: utf-8
import requests
from lxml import html
from bs4 import BeautifulSoup
import requests.exceptions
import re


def isEmailValid(string):
    return (
        'wix' not in string and
        (
            string.endswith('.com') or
            string.endswith('.org') or
            string.endswith('.eu') or
            string.endswith('.bzh') or
            string.endswith('.fr')
        )
    )


def getAllLinks(url):
    href = []
    try:
        page = requests.get(url)
        if page:
            tree = html.fromstring(page.content)
            href = tree.xpath('//a/@href')
            return list(set(href))
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(e)
        return list(set(href))
    except requests.exceptions.RequestException as e:
        print(e)
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
    if 'mailto' not in url:
        response = requests.get(
            url,
            allow_redirects=True
        ).content
        soup = BeautifulSoup(response, "html.parser")
        email = soup(
            text=re.compile(r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*')
        )
        string = str(email)
        curedString = string.replace("\\t", "")
        curedString = curedString.replace("\\n", "")
        curedString = curedString.replace("\\r", "")
        _emailtokens = curedString.split(' ')
        if len(_emailtokens):
            results = [
                match.group(0) for token in _emailtokens for match in [
                    re.search(
                        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
                        str(token.strip())
                    )
                ] if match
            ]
            for item in results:
                if (isEmailValid(item)):
                    print('email validated : '+item)
                    finalMailing.append(item)
                else:
                    print('email not validated : '+item)
    return list(set(finalMailing))
