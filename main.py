# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from tinydb import TinyDB, Query
from organisation import Organisation
import requests
import re
import webModule
import time

AGENDA_TRAD_PREFIX_URL = 'https://agendatrad.org/'
TAMM_KREIZ_PREFIX_URL = 'https://www.tamm-kreiz.bzh/'
TAMM_KREIZ_POSTFIX = 'liste-lettre/15/'

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

contactList = []
urlTab = {}


def getAgendaTradPageListDetails(url, database, urlList):
    href = webModule.getAllLinks(AGENDA_TRAD_PREFIX_URL+url)
    for item in href:
        if (
            item.startswith('/orga_association/') or
            item.startswith('/orga_autre/')
        ):
            getOrgaDetailsAgendaTrad(item, database, urlList)


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


def getOrgaOldDates(tree, url):
    # Verification des anciennes dates
    contact_url = url[:-5]+'/oldEvent.html'
    page_contact = requests.get(contact_url)
    contact_tree = html.fromstring(page_contact.content)
    return contact_tree.xpath('//*[contains(@class, "date_head")]/text()')


def getOrgaDetailsAgendaTrad(url, database, urlList):
    newContact = {}
    newUrl = {}
    newUrl['address'] = AGENDA_TRAD_PREFIX_URL+url
    urlDatabaseQuery = Query()
    if len(urlList.search(urlDatabaseQuery.address == newUrl['address'])) == 0:
        urlList.insert(newUrl)
        page = requests.get(newUrl['address'])
        tree = html.fromstring(page.content)
        organisation = Organisation()
        # newContact['source'] = 'agendaTrad'
        organisation.setSource('agendaTrad')
        organisation.setName(
            tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0]
        )
        organisation.setAddress(getOrgaAddress(tree))
        # newContact['address'] = getOrgaAddress(tree)
        # Verification du site de l'asso
        addressMailList = webModule.getMailTabFromWebsite(
            newUrl['address'][:-5] + '/contact.html'
        )
        print(addressMailList)
        isThereAWebsite = tree.xpath('//a[@class="btn btn-small"]/@href')

        if len(isThereAWebsite) > 0:
            if 'https://www.facebook.com/' in isThereAWebsite[0]:
                organisation.setFacebook(isThereAWebsite[0])
                # newContact['facebookPages'] =
            else:
                organisation.setWebsite(isThereAWebsite[0])
                organisation.setMail(
                    webModule.searchForMailInWebsite(
                        organisation.getWebsite()
                    )
                )

        if len(getOrgaOldDates(tree, newUrl['address'])) > 0:
            organisation.setLastEventDate(
                getOrgaOldDates(
                    tree,
                    newUrl['address'])[0]
                )
        else:
            newContact['last-event-date'] = 'none'
        # Adding organisation to database if she has already make some events

        if organisation.hasDoneConcert():
            contactList.append(newContact)
            Orga = Query()
            if len(database.search(Orga.name == organisation.getName())) == 0:
                database.insert(organisation.toDict())
                organisation.display()


def getAllMail(database):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):
        result = result + item['mail-address']
    return list(set(result))


def displayAllMail(databaseTK, databaseAT):
    mailAT = getAllMail(databaseAT)
    mailTK = getAllMail(databaseTK)
    print(mailAT)
    print(mailTK)
    mailInTkAndInAT = 0
    newMail = 0
    doublons = []
    newMails = []
    for item in mailTK:
        item = item.replace('\r', "")
        if item in mailAT:
            mailInTkAndInAT = mailInTkAndInAT + 1
            doublons.append(item)
        else:
            newMails.append(item)
            newMail = newMail + 1
    percentageDoublon = (mailInTkAndInAT * 100)/len(mailTK)
    print("================================================")
    print("Emails from Tamm Kreizh : " + str(len(mailTK)))
    print("Emails from Agenda Trad : " + str(len(mailTK)))
    print('Doublons = ' + str(mailInTkAndInAT))
    print('Pourcentage de doublons : ' + str(percentageDoublon))


def parseAgendaTrad(database, urlExplored):
    for i in range(1, 27):
        getAgendaTradPageListDetails(
            'organisateurs/France?page='+str(i), database, urlExplored
        )


def getAnnuaireTammKreizhUrlList():
    links = []
    for item in TAMM_KREIZ_POSTFIX_URL_LIST:
        for link in webModule.getAllLinks(TAMM_KREIZ_PREFIX_URL+item):
            if '/annuaire_entree' in link:
                links.append(link)
    return list(set(links))


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


def parseTammKreizh(orgaDatabase, urlExplored):
    links = getAnnuaireTammKreizhUrlList()
    for link in links:
        # searching for all : listingitemitemtitleaddress
        urlToExplore = TAMM_KREIZ_PREFIX_URL+link
        urlDatabaseQuery = Query()
        newUrl = {}
        if len(urlExplored.search(urlDatabaseQuery.address == link)) == 0:
            newUrl['address'] = link
            urlExplored.insert(newUrl)
            page = requests.get(urlToExplore)
            tree = html.fromstring(page.content)
            info = TammKreizhGetInfoFromeTree(tree)
            orga = Organisation()
            orga.setSource(TAMM_KREIZ_PREFIX_URL)
            name = TammKreizhGetNameFromeTree(tree)
            orga.setName(name[0])
            for item in info:
                item = item.replace("\\n", "")
                item = item.replace("\\t", "")
                item = item.replace("\\r", "")
                pattern = re.compile('[@_!#$%^&*()<>?}{~:]')
                if pattern.search(item) is not None:
                    orga.addMail(item)
                if item.startswith('0'):
                    orga.setPhoneNumber(item)
            website = TammKreizhGetWebsiteFromeTree(tree)
            for item in website:
                if 'facebook' in item:
                    orga.setFacebook(item)
                else:
                    orga.setWebsite(item)
                    orga.setMail(
                        webModule.searchForMailInWebsite(orga.getWebsite())
                    )
            Orga = Query()
            if len(orgaDatabase.search(Orga.name == orga.getName())) == 0:
                orgaDatabase.insert(orga.toDict())
            orga.display()


def main():
    #
    dbAgendaTrad = TinyDB('db/databaseAgendaTrad.json')
    OrgaAgendaTrad = dbAgendaTrad.table('Orga')
    urlExploredAgendaTrad = dbAgendaTrad.table('website')

    dbTammKreizh = TinyDB('db/databaseTammKreizh.json')
    OrgaTammKreizh = dbTammKreizh.table('Orga')
    urlExploredTammKreizh = dbTammKreizh.table('website')

    parseAgendaTrad(OrgaAgendaTrad, urlExploredAgendaTrad)
    parseTammKreizh(OrgaTammKreizh, urlExploredTammKreizh)

    # mailList = displayAllMail(OrgaAgendaTrad)
    displayAllMail(OrgaTammKreizh, OrgaAgendaTrad)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
