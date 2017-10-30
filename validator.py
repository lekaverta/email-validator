#INSPIRED http://verifalia.com/validate-email
#IF JUST FOR USE IN LISTS, ITS NOT NECESSARY PROXY, WE USE N RCPT IN ONE CONNECTION

import telnetlib
import time
import dns.resolver
import csv
import numpy
from itertools import groupby

class Email:
    valid = None
    erro = False
    status = None
    address = None
    line = []

    def __init__(self, address, line):
        self.address = address
        self.line = line

    def set_status(self, status):
        self.status = status

        if self.status == '503':
            self.erro = True
            self.valid = None
        elif self.status == '550':
            self.erro = False
            self.valid = False
        #DOMAIN WITHOUT MX
        elif self.status == '999':
            self.erro = False
            self.valid = False
        #DOMAIN WITH MX OK
        elif self.status == '222':
            self.erro = True
            self.valid = True
        elif self.status.startswith('2'):
            self.erro = False
            self.valid = True
        else:
            self.erro = True
            self.valid = None

    def get_domain(self):
        return self.address.split('@')[1]

    def __str__(self):
     return "{} >> valid: {} - status: {}".format(self.address, self.valid, self.status)

class EmailsFile:
    emails = []
    indexEmail = -1
    path = None
    emailColumn = None
    head = []
    sanitized_path = None
    invalid_path = None

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
                    self.emails.append(Email(row[self.indexEmail], row))
                
                cont += 1
            
    def _get_email_index(self, row):
        self.head = row

        for index, column in enumerate(row):
            if (column == self.emailColumn):
                self.indexEmail = index

    def _group_emails_by_domain(self):
        emailsOrdered = []
        self.emails = sorted(self.emails, key = lambda e: e.address.lower().split('@')[1])

        for key, group in groupby(self.emails, key = lambda e: e.address.lower().split('@')[1]):
            emailsOrdered.append(list(group))  

        self.emails = emailsOrdered

    def _generate_paths(self):
        dirs = self.path.split('/')
        fileName = dirs[len(dirs) - 1]
        dirs = numpy.delete(dirs, len(dirs) - 1)
        self.sanitized_path = "{}/sanitized_{}".format('/'.join(dirs), fileName)
        self.invalid_path = "{}/invalids_{}".format('/'.join(dirs), fileName)

    def _generate_file(self, path, emails):
        with open(path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(self.head)

            for email in emails:
                spamwriter.writerow(email.line)
            
    def generate_sanitized_output(self):
        self._generate_paths()
        emails_to_file = []

        for emails in self.emails:
                for email in emails:
                    if (email.valid):
                        emails_to_file.append(email)
        
        self._generate_file(self.sanitized_path, emails_to_file)
        return self.sanitized_path

    def generate_invalids_output(self):
        self._generate_paths()
        emails_to_file = []

        for emails in self.emails:
                for email in emails:
                    if (email.valid == False):
                        emails_to_file.append(email)
        
        self._generate_file(self.invalid_path, emails_to_file)
        return self.invalid_path

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
    validate_just_domains = False

    def __init__(self, emails, domain, just_domains):
        self.emails = emails
        self.domain = domain  
        self.validate_just_domains = just_domains
    
    def validate_all(self):
        self._get_host_mx_domain()

        if self.host is not None:            
            if self.validate_just_domains == False:
                self._open_telnet()
                self._register_domain()
                self._register_sender()    

            for email in self.emails:
                if self.validate_just_domains:
                    email.set_status('222')
                else:
                    self._validate_email(email)

            if self.session is not None:
                self.session.close()
        else:
            for email in self.emails:
                email.set_status('999')

    def _get_host_mx_domain(self):
        preference = 0

        try:
            answers = dns.resolver.query(self.domain, 'MX')
            for rdata in answers:
                if preference < rdata.preference:
                    self.host = rdata.exchange 
        except:
            self.host = None

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
        self.session.write(('RCPT TO: <{}>'.format(email.address)).encode(self.encode) + self.wordwrap)
        check = self.session.read_until(self.endprocessmark, self.timeout)
        email.set_status(check[0:3])
