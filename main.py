# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from tinydb import TinyDB, Query
from organisation import Organisation
import concurrent.futures
import requests
import re
import webModule
import time
import sys

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


def getAgendaTradPageListDetails():
    # getting all url in AgendaTradToExplore
    result = []
    for i in range(1, 27):
        href = webModule.getAllLinks(AGENDA_TRAD_PREFIX_URL+'organisateurs/France?page='+str(i))
        for item in href:
            if (
                item.startswith('/orga_association/') or
                item.startswith('/orga_autre/')
            ):
                result.append(item)
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
        isThereAWebsite = tree.xpath('//a[@class="btn btn-small"]/@href')

        if len(isThereAWebsite) > 0:
            if 'https://www.facebook.com/' in isThereAWebsite[0]:
                organisation.setFacebook(isThereAWebsite[0])
                # newContact['facebookPages'] =
            else:
                organisation.setWebsite(isThereAWebsite[0])

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
def updateDatabaseAddingMails(database):
    Orga = Query()
    result = []
    docs =  database.search(Orga['website'].exists())
    for item in docs:
        item['mail-address'] = webModule.searchForMailInWebsite(item['website'])
    database.write_back(docs)


def getAllMailFromWebsiteInDatabase(database):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):
        result = result + item['mail-address']
    return list(set(result))




def displayAllMail(databaseTK, databaseAT):
    mailAT = getAllMailFromWebsiteInDatabase(databaseAT)
    mailTK = getAllMailFromWebsiteInDatabase(databaseTK)
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
    print("Emails from Agenda Trad : " + str(len(mailAT)))
    print('Doublons = ' + str(mailInTkAndInAT))
    print('Pourcentage de doublons : ' + str(percentageDoublon))
    print("================================================")


def parseAgendaTrad(database, urlExplored):
        for item in getAgendaTradPageListDetails():
            getOrgaDetailsAgendaTrad(item, database, urlList)


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

def parseTammKreizhUrl(url, orgaDatabase, urlExplored):
    # searching for all : listingitemitemtitleaddress
    urlToExplore = TAMM_KREIZ_PREFIX_URL+url
    urlDatabaseQuery = Query()
    newUrl = {}

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
    orga.setSourceUrl(url)
    return orga

def parseTammKreizh(orgaDatabase, urlExplored):
    links = getAnnuaireTammKreizhUrlList()
    print("test")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(parseTammKreizhUrl, url, orgaDatabase, urlExplored): url for url in links}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                orga = future.result()
                orga.display()
                Orga = Query()
                urlDatabaseQuery = Query()
                urlExplored = orga.getSourceUrl()

                if len(orgaDatabase.search(Orga.name == orga.getName())) == 0:
                    orgaDatabase.insert(orga.toDict())
                if len(urlExplored.search(urlDatabaseQuery.address == url)) == 0:
                    newUrl['address'] = url
                    urlExplored.insert(newUrl)

            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r page is %d bytes' % (url, len(data)))



def cleanDB(db):
    db.purge_table('Orga')
    db.purge_table('website')


def displayHelp():
    print('-h for help')
    print('-removeAll to remove all database')
    print('-rat remove only agenda trad db')
    print('-rtk remove only tamm kreizh db')



def main():
    # Command line manger
    dbAgendaTrad = TinyDB('db/databaseAgendaTrad.json')
    dbTammKreizh = TinyDB('db/databaseTammKreizh.json')
    OrgaAgendaTrad = dbAgendaTrad.table('Orga')
    urlExploredAgendaTrad = dbAgendaTrad.table('website')
    OrgaTammKreizh = dbTammKreizh.table('Orga')
    urlExploredTammKreizh = dbTammKreizh.table('website')

    if(len(sys.argv) > 1):
        if len(sys.argv) == 2:
            if sys.argv[1] == '-h' or sys.argv[1] == '--help':
                displayHelp()
                sys.exit(0)
            elif sys.argv[1] == '-removeAll':
                cleanDB(dbAgendaTrad)
                cleanDB(dbTammKreizh)
            elif sys.argv[1] == '-rat':
                cleanDB(dbAgendaTrad)
            elif sys.argv[1] == '-rtk':
                cleanDB(dbTammKreizh)
            else:
                displayHelp()
                exit(0)

    # parseAgendaTrad(OrgaAgendaTrad, urlExploredAgendaTrad)
    parseTammKreizh(OrgaTammKreizh, urlExploredTammKreizh)
    getAllMailFromWebsiteInDatabase(OrgaAgendaTrad)
    getAllMailFromWebsiteInDatabase(OrgaTammKreizh)
    # mailList = displayAllMail(OrgaAgendaTrad)
    displayAllMail(OrgaTammKreizh, OrgaAgendaTrad)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
