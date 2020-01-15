# coding: utf-8
import requests
from lxml import html
from bs4 import BeautifulSoup
import requests.exceptions
import re
import concurrent.futures
import tldextract
MAX_WORKERS = 5

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


def getUrlContent(urlToExplore):
    # searching for all : listingitemitemtitleaddress
    page = requests.get(urlToExplore, timeout=10)
    return page.content


def getAllMailsFromString(string):
    curedString = str(string)
    curedString = curedString.replace("\\t", "")
    curedString = curedString.replace("\\n", "")
    curedString = curedString.replace("\\r", "")
    curedString = re.sub(r'\s', '', curedString)
    _emailtokens = curedString.split(' ')
    finalResult = []
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
        if isEmailValid(item):
            finalResult.append(item)
    return finalResult

def getAllSubLinks(url):
    href = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(getUrlContent, url): url
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                tree = html.fromstring(future.result())
                href = tree.xpath('//a/@href')
                result = []

                subdomain = tldextract.extract(url)[0]
                for link in href:
                    if (
                        subdomain == tldextract.extract(link)[0] and
                        'jpg' not in link and
                        'pdf' not in link and
                        'facebook' not in link and
                        'instagram' not in link and
                        'youtube' not in link and
                        'vimeo' not in link and
                        'deezer' not in link and
                        '2018' not in link and
                        '2019' not in link and
                        '2020' not in link and
                        'contact' in link
                    ):
                        if link[0] == '/':
                            result.append(url+link)
                            print(url+link)
                        else:
                            result.append(link)
                            print(link)
                return list(set(result))
            except Exception:
                pass

def getAllMailToFromUrl(urlListe):
    href = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(getUrlContent, url): url for url in urlListe
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                tree = html.fromstring(future.result())
                href = tree.xpath('//a/@href')
                result = []

                subdomain = tldextract.extract(url)[0]
                for link in href:
                    regexp = re.compile(("mailto:([a-z0-9!#$%&'*+\/=?^_`{|}~-]+@[a-z0-9]+\.[a-zA-Z0-9-.]+)"))
                    links = re.findall(regexp, link)
                    print(links)
                    result = result + links
                return list(set(result))
            except Exception as e:
                print(e)
                return []

def getAllLinks(url):
    href = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(getUrlContent, url): url
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                tree = html.fromstring(future.result())
                href = tree.xpath('//a/@href')
                result = []
                for link in href:
                    result.append(link)
                return list(set(href))
            except Exception as e:
                print(e)


def searchForMailInWebsite(urlListe):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(getUrlContent, url):  url for url in urlListe
        }
        for future in concurrent.futures.as_completed(future_to_url):
            # url = future_to_url[future]
            try:
                soup = BeautifulSoup(future.result(), "html.parser")
                email = soup(
                    text=re.compile(
                        r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*'
                    )
                )
                orgaListe = getAllMailsFromString(email)
                print(orgaListe)
                return list(set(orgaListe))
            except Exception as e:
                print(e)
    return []
