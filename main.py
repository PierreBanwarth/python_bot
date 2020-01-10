# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from unidecode import unidecode
from tinydb import TinyDB, Query
from email_validator import validate_email, EmailNotValidError
from validate_email import validate_email

import requests
import sys
import re
import webModule
import io

AGENDA_TRAD_PREFIX_URL = 'https://agendatrad.org/'
contactList = []

urlTab = {}

def getPageListDetails(url, database, urlList):
    href = webModule.getAllLinks(AGENDA_TRAD_PREFIX_URL+url)
    for item in href:
        if item.startswith('/orga_association/') or item.startswith('/orga_autre/'):
            getOrgaDetailsAgendaTrad(item, database,urlList)

def validateMailList(listString):

    result = []
    for item in listString:
        try:
            v = validate_email(item) # validate and get info
            email = v["email"] # replace with normalized form
            result.append(email)
        except EmailNotValidError as e:
            pass
    return result

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
        newContact['source'] = 'agendaTrad'
        newContact['name'] = tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0]

        newContact['address'] = getOrgaAddress(tree)
        # Verification du site de l'asso

        addressMailList = webModule.getMailTabFromWebsite(newUrl['address'][:-5] + '/contact.html')
        print(addressMailList)
        isThereAWebsite = tree.xpath('//a[@class="btn btn-small"]/@href')

        if len(isThereAWebsite)>0:
            if 'https://www.facebook.com/' in isThereAWebsite[0]:
                newContact['facebookPages'] = isThereAWebsite[0]
            else:
                newContact['website'] = isThereAWebsite[0]
                addressMailList = webModule.searchForMailInWebsite(newContact['website'])
                newContact['mail-address'] = list(set(addressMailList))
        if len(getOrgaOldDates(tree, newUrl['address']))>0:
            newContact['last-event-date'] = getOrgaOldDates(tree, newUrl['address'])[0]
        else:
            newContact['last-event-date'] = 'none'
        # Adding organisation to database if she has already make some events

        if len(newContact['last-event-date']) != 0:
            contactList.append(newContact)
            Orga = Query()
            if len(database.search(Orga.name == newContact['name'])) == 0:
                database.insert(newContact)
                displayOrga(newContact)


def displayOrga(orga):
    print('========================================')
    print('Name : ' + orga['name'])
    print('From : ' + orga['source'])
    print('Address : ' + orga['address'])
    if 'last-event-date' in orga:
        print('Last event date : ')
    print('----------------------------------------')
    if 'website' in orga:
        print('Web : ' + orga['website'])
    if 'facebookPages' in orga:
        print('Facebook : ' + orga['facebookPages'])
    print('----------------------------------------')
    if 'mail-address' in orga:
        for item in orga['mail-address']:
            print(item)
    print('========================================')

def displayAllMail(database):
    Orga = Query()
    result = []
    finalMailing = []
    for item in database.search(Orga['mail-address'].exists()):
        result = result + item['mail-address']
    result = list(set(result))
    for item in result:
        if validate_email(item):
            finalMailing.append(item)
    unic = []
    # for item in database.search(Orga['mail-address'].exists()):
        # for mail in item['mail-address']:
        #     if 'wix' not in mail and not mail in unic:
        #         print(item['name'] + '   ' +mail)
        #         unic.append(mail)
    for item in database.search(Orga['facebookPages'].exists()):
        print(item['facebookPages'])
    # print(result)
    # print(len(result))
    #
    # print(finalMailing)
    # print(len(finalMailing))

    expression = re.compile(r'\.[a-zA-Z]*')
    extension = {}
    for item in finalMailing:
        extension_occurence = expression.findall(item)
        if not extension_occurence[len(extension_occurence)-1] in extension:
            extension[extension_occurence[len(extension_occurence)-1]] = 1
        else:
            extension[extension_occurence[len(extension_occurence)-1]] = extension[extension_occurence[len(extension_occurence)-1]] +1

    # print(sorted(extension.items(), key=lambda x: x[1], reverse=True))

    return result

def getAllMail(mailList, database):
    Orga = Query()
    for item in database.search(Orga.website.exists()):
        href = webModule.getAllLinks(item['website'])
        for link in href:

            addressMailList = webModule.getMailTabFromWebsite(link)
            print(addressMailList)

    return mailList

def main():
    #
    db = TinyDB('db/database.json')
    table = db.table('Orga')
    url = db.table('website')

    for i in range(1, 27):
        getPageListDetails('organisateurs/France?page='+str(i), table, url)
    mailList = displayAllMail(table)
    # getAllMail(mailList, table)

if __name__ == "__main__":
    main()
