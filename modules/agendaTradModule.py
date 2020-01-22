# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from tinydb import Query

from organisation import Organisation
import concurrent.futures
import webModule

AGENDA_TRAD_PREFIX_URL = 'https://agendatrad.org/'


def getAgendaTradPageListDetails(orgaDatabase):
    # getting all url in AgendaTradToExplore
    result = []
    Orga = Query()

    for i in range(1, 27):
        href = webModule.getAllLinks(
            AGENDA_TRAD_PREFIX_URL+'organisateurs/France?page='+str(i)
        )
        for item in href:
            if (
                item.startswith('/orga_association/') or
                item.startswith('/orga_autre/')
            ) and len(
                orgaDatabase.search(
                    Orga.sourceUrl == AGENDA_TRAD_PREFIX_URL+item
                )
            ) == 0:

                result.append(AGENDA_TRAD_PREFIX_URL+item)
    return result


def getOrgaAddress(tree):
    streetAddress = tree.xpath('//span[@itemprop="street-address"]/text()')[0]
    postalCode = tree.xpath('//span[@itemprop="postal-code"]/text()')[0]
    locality = tree.xpath('//span[@itemprop="locality"]/text()')[0]
    countryName = tree.xpath('//span[@itemprop="country-name"]/text()')[0]
    return (
        streetAddress +
        ' ' +
        locality +
        ' ' +
        postalCode +
        ' ' +
        countryName
    )


def getName(tree):
    return tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0]


def getWebsite(tree):
    return tree.xpath('//a[@class="btn btn-small"]/@href')


def getInfoFromTreeAgendaTrad(tree):
    organisation = Organisation()
    organisation.setSource('agendaTrad')
    organisation.setName(getName(tree))
    organisation.setAddress(getOrgaAddress(tree))
    # Verification du site de l'asso
    website = getWebsite(tree)

    if len(website) > 0:
        if 'https://www.facebook.com/' in website[0]:
            organisation.setFacebook(website[0])
        else:
            organisation.setWebsite(website[0])
    # Adding organisation to database if she has already make some events
    return organisation


def parseFromList(links):
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
                orga = getInfoFromTreeAgendaTrad(tree)
                orga.setSourceUrl(url)
                orgaListe.append(orga)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
    return orgaListe


def parseAgendaTrad(orgaDatabase):
    links = getAgendaTradPageListDetails(orgaDatabase)
    return parseFromList(links)
