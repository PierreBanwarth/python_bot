# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tinydb import TinyDB
import sys
sys.path.append('modules/')
import webModule
import tammKreizhModule
import agendaTradModule
import databaseModule
import time

contactList = []
urlTab = {}


def displayAllMail(database):
    print("==============Website       ====================")
    nbWebsitesAT = len(databaseModule.getAllWebsite(database, 'agendatrad'))
    nbWebsitesTK = len(databaseModule.getAllWebsite(database, 'tamm-kreiz'))
    nombreOrgaSansWebsiteAgendaTrad = len(
        databaseModule.getAllWithoutWebsite(database, 'agendatrad')
    )
    nombreOrgaSansWebsitetammkreiz = len(
        databaseModule.getAllWithoutWebsite(database, 'tamm-kreiz')
    )
    print('Website from Tamm Kreiz : ' + str(nbWebsitesTK))
    print('Website from AgendaTrad : ' + str(nbWebsitesAT))

    print('Orga Without website from Tamm Kreiz : ' + str(
        nombreOrgaSansWebsitetammkreiz
    ))
    print('Orga Without website from AgendaTrad : ' + str(
        nombreOrgaSansWebsiteAgendaTrad
    ))
    nbsites = nbWebsitesAT + nbWebsitesTK
    nbNoSites = nombreOrgaSansWebsitetammkreiz + nombreOrgaSansWebsitetammkreiz
    nbOrga = nbsites + nbNoSites
    percentageSitesAll = (nbsites * 100)/nbOrga
    nbOrgaTK = nbWebsitesTK + nombreOrgaSansWebsitetammkreiz
    nbOrgaAT = nbWebsitesAT + nombreOrgaSansWebsiteAgendaTrad
    percentageSitesTK = (nbWebsitesTK * 100)/(nbOrgaTK)
    percentageSitesAT = (nbWebsitesAT * 100)/(nbOrgaAT)

    print('Pourcentage de sites Tamm Kreiz : ' + str(percentageSitesTK))
    print('Pourcentage de sites AgendaTrad : ' + str(percentageSitesAT))
    print('Pourcentage de sites total : ' + str(percentageSitesAll))
    print("================================================")

    mailAT = databaseModule.getAllMailFromWebsiteInDatabaseFromSource(
        database,
        'agendatrad'
    )
    mailTK = databaseModule.getAllMailFromWebsiteInDatabaseFromSource(
        database,
        'tamm-kreiz'
    )

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
    newMail = getAllMailAvailableToSend(
        mailAT,
        mailTK,
        getOldMailFromMailChimp()
    )
    newOrgaList = databaseModule.getAllOrgaWithNewMail(database, newMail)
    count = 0
    f = open("db/emails_result.txt", "w")
    for item in newOrgaList:
        for mail in list(set(item['mail-address'])):
            f.write(item['name'] + " : " + mail + '\n')
            count = count + 1
    f.close()
    print("================================================")
    print('new mail = '+str(count))
    print("================================================")


def getAllMailAvailableToSend(mailAT, mailTK, OldMail):
    newMails = []
    doublonsAT = 0
    doublonsTK = 0
    for item in mailAT:
        if item in OldMail:
            doublonsAT = doublonsAT + 1
        else:
            newMails.append(item)
    for item in mailTK:
        if item in OldMail:
            doublonsTK = doublonsTK + 1
        else:
            newMails.append(item)

    print("Emails from Tamm Kreizh : " + str(len(mailTK)))
    print("Doublons from Tamm Kreiz : " + str(doublonsTK))

    print("Emails from Agenda Trad : " + str(len(mailAT)))
    print("Doublons from Agenda Trad : " + str(doublonsAT))
    print("================================================")
    print("old Mails : " + str(len(OldMail)))
    print("================================================")
    print("New Mails : " + str(len(newMails)))
    return list(set(newMails))


def cleanDB(db):
    db.purge_table('Orga')


def displayHelp():
    print('-h for help')
    print('-removeAll to remove all database')
    print('-rat remove only agenda trad db')
    print('-rtk remove only tamm kreizh db')
    print('-getData to print resume of database infos')


def getOldMailFromMailChimp():
    filepath = 'db/mails-from-mailchimp.txt'
    result = []
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            line = fp.readline()
            curedString = webModule.cureString(line)
            result.append(curedString)
    return result


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
                databaseModule.cleanMailDb(Orga)
                displayAllMail(Orga)
            else:
                displayHelp()
    else:
        orgaListe = agendaTradModule.parseAgendaTrad(Orga)
        databaseModule.insertAllInDb(orgaListe, Orga)

        print('getting orga list')
        orgaListe = tammKreizhModule.parseTammKreizh(Orga)

        print('inserting db')
        databaseModule.insertAllInDb(orgaListe, Orga)

        print('adding links to explore')
        databaseModule.updateAddingLinksToExplore(Orga)

        print('adding finded mail in db')
        databaseModule.updateDatabaseAddingMails(Orga)
        databaseModule.cleanMailDb(Orga)
        displayAllMail(Orga)
        databaseModule.updateDatabaseAddingMailsFromMailTo(Orga)
        displayAllMail(Orga)


if __name__ == "__main__":
    print(sys.getdefaultencoding())
    start_time = time.time()
    main()
    print("--- %s Minutes ---" % ((time.time() - start_time)/60))
