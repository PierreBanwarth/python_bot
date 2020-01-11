# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from unidecode import unidecode
from tinydb import TinyDB, Query
from email_validator import validate_email, EmailNotValidError
from validate_email import validate_email
from organisation import Organisation
import requests
import sys
import re
import webModule
import io

AGENDA_TRAD_PREFIX_URL = 'https://agendatrad.org/'
TAMM_KREIZ_PREFIX_URL = 'https://www.tamm-kreiz.bzh'
TAMM_KREIZ_POSTFIX_URL_LIST = ['/liste-lettre/15/1','/liste-lettre/15/A','/liste-lettre/15/B','/liste-lettre/15/C','/liste-lettre/15/D','/liste-lettre/15/E','/liste-lettre/15/F','/liste-lettre/15/G','/liste-lettre/15/H','/liste-lettre/15/I','/liste-lettre/15/J','/liste-lettre/15/K','/liste-lettre/15/L','/liste-lettre/15/M','/liste-lettre/15/N','/liste-lettre/15/O','/liste-lettre/15/P','/liste-lettre/15/Q','/liste-lettre/15/R','/liste-lettre/15/S','/liste-lettre/15/T','/liste-lettre/15/U','/liste-lettre/15/V','/liste-lettre/15/W','/liste-lettre/15/X','/liste-lettre/15/Y','/liste-lettre/15/Z']
contactList = []

urlTab = {}

def getAgendaTradPageListDetails(url, database, urlList):
    href = webModule.getAllLinks(AGENDA_TRAD_PREFIX_URL+url)
    for item in href:
        if item.startswith('/orga_association/') or item.startswith('/orga_autre/'):
            getOrgaDetailsAgendaTrad(item, database,urlList)

def getOrgaAddress(tree):
    streetAddress = tree.xpath('//span[@itemprop="street-address"]/text()')[0]
    postalCode = tree.xpath('//span[@itemprop="postal-code"]/text()')[0]
    locality = tree.xpath('//span[@itemprop="locality"]/text()')[0]
    countryName = tree.xpath('//span[@itemprop="country-name"]/text()')[0]
    return  streetAddress +' '+ locality +' '+ postalCode +' '+ countryName

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
        newContact = Organisation()
        # newContact['source'] = 'agendaTrad'
        organisation.setSource('agendaTrad')
        organisation.setName(tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0])
        organisation.setAddress(getOrgaAddress(tree))
        # newContact['address'] = getOrgaAddress(tree)
        # Verification du site de l'asso
        addressMailList = webModule.getMailTabFromWebsite(newUrl['address'][:-5] + '/contact.html')
        print(addressMailList)
        isThereAWebsite = tree.xpath('//a[@class="btn btn-small"]/@href')

        if len(isThereAWebsite)>0:
            if 'https://www.facebook.com/' in isThereAWebsite[0]:
                organisation.setFacebook(isThereAWebsite[0])
                # newContact['facebookPages'] =
            else:
                organisation.setWebsite(isThereAWebsite[0])
                organisation.setMail(webModule.searchForMailInWebsite(organisation.getWebsite()))

        if len(getOrgaOldDates(tree, newUrl['address']))>0:
            organisation.setLastEventDate(getOrgaOldDates(tree, newUrl['address'])[0])
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
    result =  []
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
        item = item.replace('\r',"")
        if item in mailAT:
            mailInTkAndInAT = mailInTkAndInAT + 1
            doublons.append(item)
        else:
            newMails.append(item)
            newMail = newMail + 1
    percentageDoublon = (mailInTkAndInAT * 100)/len(mailTK)
    print('Nouveaux Emails = ' + str(newMail))
    print('Doublons = ' + str(mailInTkAndInAT))
    print('Pourcentage de doublons : ' + str(percentageDoublon))


def parseAgendaTrad(orga, urlExplored):
    for i in range(1, 27):
        getAgendaTradPageListDetails('organisateurs/France?page='+str(i), table, url)

def getAnnuaireTammKreizhUrlList():
    links = []
    for item in TAMM_KREIZ_POSTFIX_URL_LIST:
        for link in webModule.getAllLinks(TAMM_KREIZ_PREFIX_URL+item):
            if '/annuaire_entree' in link:
                links.append(link)
    return list(set(links))

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
            test = tree.xpath('//ul[@class="listingitemitemtitleaddress"]/li/text()')
            orga = Organisation()
            orga.setSource(TAMM_KREIZ_PREFIX_URL)
            nameTest = tree.xpath('//header[@class="introblock listingitemintro"]/h1/text()')
            orga.setName(nameTest[0])
            for item in test:
                item = item.replace("\n","")
                item = item.replace("\t","")
                item = item.replace("\r","")
                pattern = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
                if pattern.search(item) != None:
                    orga.addMail(item)
                if item.startswith('0'):
                    orga.setPhoneNumber(item)
            website = tree.xpath('//a[@class="listingitemitemtitleaddress circle-chevron-arrow"]/@href')
            for item in website:
                if 'facebook' in item:
                    orga.setFacebook(item)
                else:
                    orga.setWebsite(item)
                    orga.setMail(webModule.searchForMailInWebsite(orga.getWebsite()))
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

    # parseAgendaTrad(OrgaAgendaTrad, urlExploredAgendaTrad)

    parseTammKreizh(OrgaTammKreizh, urlExploredTammKreizh)
    # mailList = displayAllMail(OrgaAgendaTrad)
    displayAllMail(OrgaTammKreizh, OrgaAgendaTrad)

if __name__ == "__main__":
    main()
