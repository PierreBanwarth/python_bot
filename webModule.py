# coding: utf-8
import requests
from lxml import html
from bs4 import BeautifulSoup
import requests.exceptions
import re
from validate_email import validate_email


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
                print('=========Email=============')
                print(item)
                print('============================')

                if validate_email(item):
                    if (
                        'wix' not in item and
                        (
                            item.endswith('.com') or
                            item.endswith('.org') or
                            item.endswith('.eu') or
                            item.endswith('.bzh') or
                            item.endswith('.fr')
                        )
                    ):
                        finalMailing.append(item)
    return list(set(finalMailing))
