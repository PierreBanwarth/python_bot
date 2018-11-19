# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from unidecode import unidecode
import requests
import sys
import re

PREFIX_URL = 'https://agendatrad.org/'
contactList = []

urlTab = {}
def getPageListDetails(url):
    page = requests.get(PREFIX_URL+url)
    tree = html.fromstring(page.content)
    href = tree.xpath('//a/@href')

    href = list(set(href))

    for item in href:
        print(item)
        if item.startswith('/orga_association/') or item.startswith('/orga_autre/'):
            getOrgaDetails(item)


def getOrgaDetails(url):
    newContact = {}
    page = requests.get(PREFIX_URL+url)
    tree = html.fromstring(page.content)
    # d1.decode("unicode_escape").encode('utf-8')
    newContact['name'] = tree.xpath('//h2[@class="entitie_name rouge"]/text()')[0]
    newContact['street-adress'] = tree.xpath('//span[@itemprop="street-address"]/text()')[0]
    newContact['postal-code'] =tree.xpath('//span[@itemprop="postal-code"]/text()')[0]
    newContact['locality'] = tree.xpath('//span[@itemprop="locality"]/text()')[0]
    newContact['country-name'] = tree.xpath('//span[@itemprop="country-name"]/text()')[0]
    # <a href="http://www.12violoneux.blogspot.com" class="btn btn-small" target="_blank"><i class="fa fa-globe"></i> Site</a>
    # Verification du site de l'asso
    test = tree.xpath('//a[@class="btn btn-small"]/@href')
    if len(test)>0:
        addressMailLit = []
        newContact['website'] = test[0]
        # Verification de l'adresse mail*
        try:
            newContactWebsite = requests.get(newContact['website'])
            contactWebsiteTree = html.fromstring(newContactWebsite.content)
            getMailTab = contactWebsiteTree.xpath('//*[contains(text(),"@")]/text()')
            for text in getMailTab:
                emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
                for email in emails:
                    if email.endswith('.com') or email.endswith('.fr') or email.endswith('.net'):
                        print email
                        addressMailLit.append(email)
        except:
            print('error while trying to reach website')
        newContact['mail-address'] = addressMailLit
    # Verification des anciennes dates
    contact_url = PREFIX_URL+url[:-5]+'/oldEvent.html'
    page_contact = requests.get(contact_url)
    contact_tree = html.fromstring(page_contact.content)
    newContact['last-event-date'] = contact_tree.xpath('//*[contains(@class, "date_head")]/text()')
    if len(newContact['last-event-date']) != 0:
        contactList.append(newContact)
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

def display(contactList):
    for item in contactList:
        displayContact(item)



def main():
    for i in range(1, 2):
        # print('--'+str(i)+'--')
        getPageListDetails('organisateurs/France?page='+str(i))
    display(contactList)

if __name__ == "__main__":
    main()
