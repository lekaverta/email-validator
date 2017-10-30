#INSPIRED http://verifalia.com/validate-email
#IF JUST FOR USE IN LISTS, ITS NOT NECESSARY PROXY, WE USE N RCPT IN ONE CONNECTION

import telnetlib
import time
import dns.resolver
import csv
from itertools import groupby

class Email:
    valido = None
    erro = False
    status = None
    endereco = None

    def __init__(self, endereco):
        self.endereco = endereco

    def set_status(self, status):
        self.status = status

        if self.status == '503':
            self.erro = True
            self.valido = None
        elif self.status == '550':
            self.erro = False
            self.valido = False
        elif self.status.startswith('2'):
            self.erro = False
            self.valido = True
        else:
            self.erro = True
            self.valido = None

    def get_domain(self):
        return self.endereco.split('@')[1]

    def __str__(self):
     return "{} >> valido: {} - status: {}".format(self.endereco, self.valido, self.status)

class EmailsFile:
    emails = []
    indexEmail = -1
    path = None
    emailColumn = None

    def __init__(self, path, column):
        self.path = path
        self.emailColumn = column
        self._get_emails_from_file()
        self._group_emails_by_domain()
    
    def _get_emails_from_file(self):
        cont = 0

        with open(self.path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if cont == 0:
                    self._get_email_index(row)
                elif self.indexEmail >= 0:
                    self.emails.append(Email(row[self.indexEmail]))
                
                cont += 1
            
    def _get_email_index(self, row):
        for index, column in enumerate(row):
            if (column == self.emailColumn):
                self.indexEmail = index

    def _group_emails_by_domain(self):
        emailsOrdered = []
        self.emails = sorted(self.emails, key = lambda e: e.endereco.lower().split('@')[1])

        for key, group in groupby(self.emails, key = lambda e: e.endereco.lower().split('@')[1]):
            emailsOrdered.append(list(group))  

        self.emails = emailsOrdered

    #TODO: Write file result with status and code (.csv)
    def refresh(self):
        for emails in self.emails:
            for email in emails:
                print(email)

class EmailValidator:
    port = 25
    timeout = 5
    encode = 'ascii'
    wordwrap = '\r\n'
    endprocessmark = '/r/n/r/n#>'
    session = None
    domain = None
    emails = []
    host = None

    def __init__(self, emails, domain):
        self.emails = emails
        self.domain = domain  
    
    def validate_all(self):
        self._get_host_mx_domain()

        if self.host is not None:
            self._open_telnet()
            self._register_domain()
            self._register_sender()    

            for email in self.emails:
                self._validate_email(email)

            self.session.close()
        else:
            raise Exception("Error getting mx host")

    def _get_host_mx_domain(self):
        preference = 0

        answers = dns.resolver.query(self.domain, 'MX')
        for rdata in answers:
            if preference < rdata.preference:
                self.host = rdata.exchange 

        if self.host != None:
            self.host = self.host[:-1]
            self.host = '.'.join(str(c) for c in self.host)

    def _open_telnet(self):
        self.session = telnetlib.Telnet()
        self.session.open(self.host,
                    port = self.port,
                    timeout = self.timeout)
        self.session.write(self.wordwrap)

    def _register_domain(self):
        self.session.write(('helo {}'.format(self.domain)).encode(self.encode) + self.wordwrap)
        self.session.read_until(self.endprocessmark, self.timeout)

    def _register_sender(self):
        self.session.write(('MAIL FROM: <someone@gmail.com>').encode(self.encode) + self.wordwrap)
        self.session.read_until(self.endprocessmark, self.timeout)

    def _validate_email(self, email):
        self.session.write(('RCPT TO: <{}>'.format(email.endereco)).encode(self.encode) + self.wordwrap)
        check = self.session.read_until(self.endprocessmark, self.timeout)
        email.set_status(check[0:3])
