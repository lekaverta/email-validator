import dns.resolver

answers = dns.resolver.query('b2egroup.com.br', 'MX')
for rdata in answers:
    print("Host {} has preference {}".format(rdata.exchange, rdata.preference))