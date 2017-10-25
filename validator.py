import telnetlib
import time

#TODO: GET FROM nslookup -q=mx
host = 'gmail-smtp-in.l.google.com'
domain = 'gmail.com'

port = 25
timeout = 5
encode = 'ascii'
wordwrap = '\r\n'
endprocessmark = '/r/n/r/n#>'

#TODO: GET FROM CSV FILE
emails = ['leticia.verta@gmail.com', 'leticia.verta1@gmail.com', 'thais.mf201@gmail.com', 'thais.mf20@gmail.com', 'thaismf20@gmail.com']

start = time.time()

session = telnetlib.Telnet()
session.open(host,
             port = port,
             timeout = timeout)
session.write(wordwrap)

session.write(('helo {}'.format(domain)).encode(encode) + wordwrap)
session.write(('MAIL FROM: <someone@test.com>').encode(encode) + wordwrap)

end = time.time()
print('telnet ok: {}'.format(end - start))

for email in emails:
    start = time.time()
    session.write(('RCPT TO: <{}>'.format(email)).encode(encode) + wordwrap)
    check = session.read_until(endprocessmark, timeout)
    end = time.time()

    result = 'invalido'
    if check.startswith('2'): 
        result = 'valido'

    print('{} -> {} ({})'.format(email, result, (end - start)))

session.close()