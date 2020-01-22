from tinydb import Query
import webModule


def insertAllInDb(listeOrga, database):
    Orga = Query()
    for organisation in listeOrga:
        if len(database.search(Orga.name == organisation.getName())) == 0:
            database.insert(organisation.toDict())
            organisation.display()


def updateAddingLinksToExplore(database):
    Orga = Query()
    docs = database.search(Orga['website'] != 'not found')
    for item in docs:
        if item['website']:
            item['linksToExlpore'] = webModule.getAllSubLinks(
                item['website']
            )
        if item['linksToExlpore']:
            item['linksToExlpore'].append(item['website'])
            print(item['linksToExlpore'])
    database.write_back(docs)


def updateDatabaseAddingMailsFromMailTo(database):
    Orga = Query()
    docs = database.search(Orga['website'] != 'not found')
    for item in docs:
        if item['linksToExlpore']:
            newResult = webModule.getAllMailToFromUrl(
                item['linksToExlpore']
            )
            if item['mail-address']:
                item['mail-address'] = item['mail-address'] + newResult
            else:
                item['mail-address'] = newResult

            print(item['mail-address'])
    database.write_back(docs)


def cleanMailDb(database):
    Orga = Query()
    docs = database.search(Orga['website'] != 'not found')
    for item in database.search(Orga['mail-address'].exists()):
        item['mail-address'] = list(set(item['mail-address']))
    database.write_back(docs)


def updateDatabaseAddingMails(database):
    Orga = Query()
    docs = database.search(Orga['website'] != 'not found')
    for item in docs:
        if item['linksToExlpore']:
            item['mail-address'] = webModule.searchForMailInWebsite(
                item['linksToExlpore']
            )
            print(item['mail-address'])
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


def getAllOrgaWithNewMail(database, source):
    Orga = Query()
    result = []
    for item in database.search(Orga['mail-address'].exists()):
        found = False
        for mail in item['mail-address']:
            found = found or mail in source
        if found:
            result.append(item)
    return result
