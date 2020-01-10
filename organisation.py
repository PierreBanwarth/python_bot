class Organisation:
    def __init__(self):
        self.source = 'not found'
        self.name = 'not found'
        self.address = 'not found'
        self.facebookPages = 'not found'
        self.mailAddress = []
        self.website = 'not found'
        self.lastEventDate = 'not found'
        self.phoneNumber = 'not found'

    def setSource(self, s):
        self.source = s
    def setName(self, s):
        self.name = s
    def getName(self):
        return self.name
    def setAddress(self, s):
        self.address = s
    def setFacebook(self, s):
        self.facebookPages = s
    def addMail(self, m):
        self.mailAddress.append(m)
    def setMail(self, s):
        self.mailAddress = self.mailAddress + s
        self.mailAddress = list(set(self.mailAddress))
    def setWebsite(self, s):
        self.website = s
    def getWebsite(self):
        return self.website
    def getMail(self):
        return self.mail
    def setPhoneNumber(self, s):
        self.phoneNumber = s
    def setLastEventDate(self, s):
        self.lastEventDate = s
    def hasDoneConcert(self):
        return 'not found' in self.lastEventDate

    def display(self):
        print('================================')
        if 'not found' not in self.source:
            print('Source : '+self.source)
        if 'not found' not in self.name:
            print('Name : '+self.name)

        if 'not found' not in self.address:
            print('address : '+self.address)

        if 'not found' not in self.facebookPages:
            print('facebook : '+self.facebookPages)
        if len(self.mailAddress)>0:
            for item in self.mailAddress:
                print('mail : '+ item)
        if 'not found' not in self.website:
            print('website : '+self.website)
        if 'not found' not in self.lastEventDate:
            print('lastEventDate : '+self.lastEventDate)
        if 'not found' not in self.phoneNumber:
            print('phone number : '+ self.phoneNumber)
        print('================================')

    def toDict(self):
        result = {}
        result['source'] = self.source
        result['name'] = self.name
        result['address'] = self.address
        result['facebookPages'] = self.facebookPages
        result['mail-address'] = self.mailAddress
        result['website'] = self.website
        result['last-event-date'] = self.lastEventDate
        return result
