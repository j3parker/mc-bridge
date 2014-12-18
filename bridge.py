#!/usr/bin/env python
import re
import sys
import threading
import time


def follow(file):
	file.seek(0, 2)
	while True:
		line = file.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

def minecraftToIrc():
	lines = follow(open(mcDir + '/out'))
	regex = re.compile('\[\d+:\d+:\d+\] \[Server thread/INFO\]: <([^>]*)> (.*)$')
	for line in lines:
		m = regex.search(line)
		if not(m):
			continue
		name = m.groups()[0]
		text = m.groups()[1]
		irc = open(ircDir + '/in', 'w')
		irc.write('<' + name + '> ' + text + '\n')
		irc.close()

def ircToMinecraft():
	lines = follow(open(ircDir+ '/out'))
	regex = re.compile('\d+-\d+-\d+ \d+:\d+ <([^>]+)> (.*)')
	for line in lines:
		m = regex.search(line)
		if not(m):
			continue
		name = m.groups()[0]
		text = m.groups()[1]

		if name == 'minecraft':
			continue

		mc = open(mcDir + '/in', 'w')
		mc.write('/say ' + name + ': ' + text + '\n')
		mc.close()

		time.sleep(1) # what am i doinggggggggg weird behaviour hacks

		mc = open(mcDir + '/in', 'w')
		mc.write('\n')
		mc.close()

mcDir = sys.argv[1]
ircDir = sys.argv[2]

if __name__ == '__main__':
	t1 = threading.Thread(target = minecraftToIrc)
	t1.daemon = True
	t1.start()
	t2 = threading.Thread(target = ircToMinecraft)
	t2.daemon = True
	t2.start()
	while True:
		time.sleep(10)
