# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from tinydb import Query

from organisation import Organisation
import concurrent.futures
import re
import webModule

TAMM_KREIZ_PREFIX_URL = 'https://www.tamm-kreiz.bzh'
TAMM_KREIZ_POSTFIX = '/liste-lettre/15/'

TAMM_KREIZ_ALPHABET = [
    '1',
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z'
]
TAMM_KREIZ_POSTFIX_URL_LIST = []
for item in TAMM_KREIZ_ALPHABET:
    TAMM_KREIZ_POSTFIX_URL_LIST.append(TAMM_KREIZ_POSTFIX+item)


def TammKreizhGetNameFromeTree(tree):
    return tree.xpath(
        '//header[@class="introblock listingitemintro"]/h1/text()'
    )


def TammKreizhGetInfoFromeTree(tree):
    return tree.xpath(
        '//ul[@class="listingitemitemtitleaddress"]/li/text()'
    )


def TammKreizhGetWebsiteFromeTree(tree):
    return tree.xpath(
        '//a[@class="listingitemitemtitleaddress circle-chevron-arrow"]/@href'
    )


def getAnnuaireTammKreizhUrlList(database):
    links = []
    Orga = Query()
    for item in TAMM_KREIZ_POSTFIX_URL_LIST:
        for link in webModule.getAllLinks(TAMM_KREIZ_PREFIX_URL+item):
            if '/annuaire_entree' in link and len(
                database.search(Orga.sourceUrl == TAMM_KREIZ_PREFIX_URL+item)
            ) == 0:
                links.append(TAMM_KREIZ_PREFIX_URL+link)
    return list(set(links))


def getInfoFromTreeTammKreizh(tree):

    info = TammKreizhGetInfoFromeTree(tree)
    orga = Organisation()
    orga.setSource(TAMM_KREIZ_PREFIX_URL)
    name = TammKreizhGetNameFromeTree(tree)
    orga.setName(name[0])
    for item in info:
        result = webModule.getAllMails(item)
        orga.setMail(result)
        string = re.sub(r'\s', '', item)
        if string.startswith('0'):
            orga.setPhoneNumber(string)

    website = TammKreizhGetWebsiteFromeTree(tree)
    for item in website:
        if 'facebook' in item:
            orga.setFacebook(item)
        else:
            orga.setWebsite(item)
    return orga


def parseTammKreizh(orgaDatabase):
    links = getAnnuaireTammKreizhUrlList(orgaDatabase)
    orgaListe = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(webModule.getUrlContent, url): url for url in links
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                tree = html.fromstring(future.result())
                orga = getInfoFromTreeTammKreizh(tree)
                orga.setSourceUrl(url)
                orgaListe.append(orga)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
    return orgaListe
