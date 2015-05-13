#!/usr/bin/env python
#

import sys, os, string, re

def usage():
    print """\
  usage:  genserv < /etc/services > libc/netbsd/net/services.h

  this program is used to generate the hard-coded internet service list for the
  Bionic C library.
"""

re_service = re.compile(r"([\d\w\-_]+)\s+(\d+)/(tcp|udp)(.*)")
re_alias   = re.compile(r"([\d\w\-_]+)(.*)")

class Service:
    def __init__(self,name,port,proto):
        self.name    = name
        self.port    = port
        self.proto   = proto
        self.aliases = []

    def add_alias(self,alias):
        self.aliases.append(alias)

    def __str__(self):
        result  = "\\%0o%s" % (len(self.name),self.name)
        result += "\\%0o\\%0o" % (((self.port >> 8) & 255), self.port & 255)
        if self.proto == "tcp":
            result += "t"
        else:
            result += "u"

        result += "\\%0o" % len(self.aliases)
        for alias in self.aliases:
            result += "\\%0o%s" % (len(alias), alias)

        return result

def parse(f):
    result = []  # list of Service objects
    for line in f.xreadlines():
        if len(line) > 0 and line[-1] == "\n":
            line = line[:-1]
        if len(line) > 0 and line[-1] == "\r":
            line = line[:-1]

        line = string.strip(line)
        if len(line) == 0 or line[0] == "#":
            continue

        m = re_service.match(line)
        if m:
            service = Service( m.group(1), int(m.group(2)), m.group(3) )
            rest    = string.strip(m.group(4))

            while 1:
                m = re_alias.match(rest)
                if not m:
                    break
                service.add_alias(m.group(1))
                rest = string.strip(m.group(2))

            result.append(service)

    return result

services = parse(sys.stdin)
line = '/* generated by genserv.py - do not edit */\nstatic const char  _services[] = "\\\n'
for s in services:
    line += str(s)+"\\\n"
line += '\\0";\n'
print line