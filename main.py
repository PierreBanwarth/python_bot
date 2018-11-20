# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from unidecode import unidecode
from tinydb import TinyDB, Query

import requests
import sys
import re
import webModule

PREFIX_URL = 'https://agendatrad.org/'
contactList = []

urlTab = {}
def getPageListDetails(url, database):

    href = webModule.getAllLinks(PREFIX_URL+url)
    for item in href:
        print(item)
        if item.startswith('/orga_association/') or item.startswith('/orga_autre/'):
            getOrgaDetails(item, database)


def getOrgaDetails(url, database):
    newContact = {}
    page = requests.get(PREFIX_URL+url)
    tree = html.fromstring(page.content)

    newContact['name'] = tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0]
    newContact['street-adress'] = tree.xpath('//span[@itemprop="street-address"]/text()')[0]
    newContact['postal-code'] =tree.xpath('//span[@itemprop="postal-code"]/text()')[0]
    newContact['locality'] = tree.xpath('//span[@itemprop="locality"]/text()')[0]
    newContact['country-name'] = tree.xpath('//span[@itemprop="country-name"]/text()')[0]
    # Verification du site de l'asso
    test = tree.xpath('//a[@class="btn btn-small"]/@href')
    if len(test)>0:
        newContact['website'] = test[0]
        # Verification de l'adresse mail*
        addressMailLit = webModule.getMailTabFromWebsite(newContact['website'])
        newContact['mail-address'] = addressMailLit
    # Verification des anciennes dates
    contact_url = PREFIX_URL+url[:-5]+'/oldEvent.html'
    page_contact = requests.get(contact_url)
    contact_tree = html.fromstring(page_contact.content)
    newContact['last-event-date'] = contact_tree.xpath('//*[contains(@class, "date_head")]/text()')
    # Adding organisation to database if she has already make some events
    if len(newContact['last-event-date']) != 0:
        contactList.append(newContact)
        Orga = Query()
        if len(database.search(Orga.name == newContact['name'])) == 0:
            database.insert(newContact)
        else:
            print 'Organisation already recorded'
    # displayContact(newContact)

def displayContact(item):
    print item['name']
    print item['street-adress']
    if item.has_key('website'):
        print item['website']
    print item['locality'] + ' ' + item['postal-code'] + ' ' + item['country-name']
    if item.has_key('last-event-date') and len(item['last-event-date'])>0:
        print item['last-event-date'][0]
    if item.has_key('mail-address'):
        print item['mail-address']
def displayAllMail(database):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):
        result = result + item['mail-address']
    print list(set(result))

def getAllMail(database):
    Orga = Query()
    for item in database.search(Orga.website.exists()):
        href = webModule.getAllLinks(item['website'])
        print(href)
        for link in href:
            addressMailLit = webModule.getMailTabFromWebsite(link)
            print addressMailLit

def main():
    #
    db = TinyDB('db/database.json')
    table = db.table('Orga')

    # for i in range(3, 23):
    #     getPageListDetails('organisateurs/France?page='+str(i), table)
    displayAllMail(table)
    # getAllMail(table)

if __name__ == "__main__":
    main()