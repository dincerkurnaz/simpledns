import socket
from dnslib import DNSRecord, DNSHeader, RR, QTYPE, A
from dnslib.server import DNSServer, BaseResolver
import dns.resolver

class CustomResolver(BaseResolver):
    def __init__(self):
        self.resolved_ip = self.resolve_ip("www-turk.sm.mncdn.com") #Burasi degisecek!!!
        print(f"[+] Resolved www-turk.sm.mncdn.com to {self.resolved_ip}")
        self.external_resolver = dns.resolver.Resolver()
        self.external_resolver.nameservers = ['8.8.8.8']

    def resolve_ip(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return "127.0.0.1"

    def resolve(self, request, handler):
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        print(f"[>] Query for: {qname} ({qtype})")

        reply = request.reply()

        if str(qname) == "www.turk.net." and qtype == "A": #Burasi degisecek!!!
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(self.resolved_ip), ttl=60))
            print(f"[<] Answering with: {self.resolved_ip}")
        else:
            try:
                answer = self.external_resolver.resolve(str(qname), 'A')
                for rdata in answer:
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(rdata.address), ttl=60))
                    print(f"[<] External answer from 8.8.8.8: {rdata.address}")
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                print("[x] No answer or NXDOMAIN")
                pass

        return reply

if __name__ == '__main__':
    resolver = CustomResolver()
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    print("[*] DNS server started on port 53 (UDP)")
    server.start()

