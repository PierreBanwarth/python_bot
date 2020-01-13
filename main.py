# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import html
from tinydb import TinyDB, Query

from organisation import Organisation
import concurrent.futures
import requests
import re
import webModule
import tammKreizhModule
import agendaTradModule
import time
import sys



contactList = []
urlTab = {}

def updateDatabaseAddingMails(database):
    Orga = Query()
    docs = database.search(Orga['website'] != 'not found')
    for item in docs:
        item['mail-address'] = webModule.searchForMailInWebsite(
            item['website']
        )
    database.write_back(docs)


def getAllMailFromWebsiteInDatabase(database):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):

        result = result + item['mail-address']
    return list(set(result))


def getAllMailFromWebsiteInDatabaseFromSource(database, source):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):
        if source in item['sourceUrl']:
            result = result + item['mail-address']
    return list(set(result))

def getAllWebsite(database, source):
    Orga = Query()
    result = []
    for item in database.search(Orga['sourceUrl'].exists()):
        if source in item['sourceUrl']:
            if item['website'] != 'not found':
                result.append(item['website'])
    return list(set(result))

def getAllWithoutWebsite(database, source):
    Orga = Query()
    result = []
    for item in database.search(Orga['sourceUrl'].exists()):
        if source in item['sourceUrl']:
            if item['website'] == 'not found':
                result.append(item['website'])
    return result

def displayAllMail(database):
    print("==============Website       ====================")
    nbWebsitesAT= len(getAllWebsite(database, 'agendatrad'))
    nbWebsitesTK = len(getAllWebsite(database, 'tamm-kreiz'))
    nombreOrgaSansWebsiteAgendaTrad = len(getAllWithoutWebsite(database, 'agendatrad'))
    nombreOrgaSansWebsitetammkreiz = len(getAllWithoutWebsite(database, 'tamm-kreiz'))
    print('Website from Tamm Kreiz : '+ str(nbWebsitesTK))
    print('Website from AgendaTrad : '+ str(nbWebsitesAT))

    print('Orga Without website from Tamm Kreiz : '+ str(nombreOrgaSansWebsitetammkreiz))
    print('Orga Without website from AgendaTrad : '+ str(nombreOrgaSansWebsiteAgendaTrad))
    nbsites = nbWebsitesAT + nbWebsitesTK
    nbNoSites = nombreOrgaSansWebsitetammkreiz + nombreOrgaSansWebsitetammkreiz
    nbOrga = nbsites + nbNoSites
    percentageSitesAll = (nbsites * 100)/nbOrga
    percentageSitesTK = (nbWebsitesTK * 100)/(nbWebsitesTK+nombreOrgaSansWebsitetammkreiz)
    percentageSitesAT = (nbWebsitesAT * 100)/(nbWebsitesAT+nombreOrgaSansWebsiteAgendaTrad)


    print('Pourcentage de sites Tamm Kreiz : ' + str(percentageSitesTK))
    print('Pourcentage de sites AgendaTrad : ' + str(percentageSitesAT))
    print('Pourcentage de sites total : ' + str(percentageSitesAll))
    print("================================================")


    mailAT = getAllMailFromWebsiteInDatabaseFromSource(database,'agendatrad')
    mailTK = getAllMailFromWebsiteInDatabaseFromSource(database,'tamm-kreiz')

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
    
    print("Emails from Tamm Kreizh : " + str(len(mailTK)))
    print("Emails from Agenda Trad : " + str(len(mailAT)))
    print('Doublons = ' + str(mailInTkAndInAT))
    print('Pourcentage de doublons : ' + str(percentageDoublon))
    print("================================================")
    print(mailAT)
    print(mailTK)



def cleanDB(db):
    db.purge_table('Orga')


def displayHelp():
    print('-h for help')
    print('-removeAll to remove all database')
    print('-rat remove only agenda trad db')
    print('-rtk remove only tamm kreizh db')


def insertAllInDb(listeOrga, database):
    Orga = Query()
    for organisation in listeOrga:
        if len(database.search(Orga.name == organisation.getName())) == 0:
            database.insert(organisation.toDict())
            organisation.display()


def main():
    # Command line manger
    db = TinyDB('db/database.json')
    Orga = db.table('Orga')
    if(len(sys.argv) > 1):
        if len(sys.argv) == 2:
            if sys.argv[1] == '-h' or sys.argv[1] == '--help':
                displayHelp()
                sys.exit(0)
            elif sys.argv[1] == '-removeAll':
                cleanDB(db)
            elif sys.argv[1] == '-getData':
                displayAllMail(Orga)
                exit(0)
            else:
                displayHelp()
                exit(0)

    orgaListe = agendaTradModule.parseAgendaTrad(Orga)
    orgaListe = orgaListe + tammKreizhModule.parseTammKreizh(Orga)
    insertAllInDb(orgaListe, Orga)
    updateDatabaseAddingMails(Orga)
    displayAllMail(Orga)


if __name__ == "__main__":
    print(sys.getdefaultencoding())
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
