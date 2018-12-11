#!/usr/bin/python
# -*- coding: utf-8 -*-
# Запускать от root ТОЛЬКО

import	dpkt
import	pcapy
from impacket.ImpactDecoder import *

# list all the network devices

max_bytes = 1024
promiscuous = False
read_timeout = 100	# in milliseconds
packet_limit = 11	#-1 # infinite
print pcapy.findalldevs(), max_bytes, promiscuous, read_timeout
print '#'*22

def	sniff(interface = 'eth1'):
	pc = pcapy.open_live(interface, max_bytes, promiscuous, read_timeout)
	pc.setfilter('udp')
	pc.loop(packet_limit, recv_pkts) # capture packets

# callback for received packets
def	recv_pkts(hdr, data):
	packet = EthDecoder().decode(data)
	print packet
	eth = dpkt.ethernet.Ethernet(data)
	print 'eth.type',  eth.type
	ip = eth.data
	print 'ip', ip.data.dport
#	print 'eth.dst',  eth.dst
#	print 'eth.src',  eth.src

if __name__ == "__main__":
	'''
	help (pcapy)
	help (EthDecoder)
	'''
	sniff ()
