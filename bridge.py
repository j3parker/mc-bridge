#!/usr/bin/env python
import re
import sys
import threading
import time

infoCount = 0
lock = threading.Lock()

def follow(file):
	file.seek(0, 2)
	while True:
		line = file.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

def sendToIrc(msg):
	irc = open(ircDir + '/in', 'w')
	irc.write(msg + '\n')
	irc.close()

def minecraftToIrc():
	global infoCount, lock

	lines = follow(open(mcDir + '/out'))
	reInfo = re.compile('^\[\d+:\d+:\d+\] \[Server thread/INFO\]: (.*)$')
	reChat = re.compile('^<([^>]*)> (.*)$')
	for line in lines:
		m = reInfo.search(line)
		if not(m):
			continue
		msg = m.groups()[0]

		# Handle "/list" output
		lock.acquire()
		try:
			if infoCount > 0:
				infoCount -= 1
				sendToIrc(msg)
				continue
		finally:
			lock.release()

		# Handle chats
		m = reInfo.search(msg)
		if not(m):
			continue
		name = m.groups()[0]
		text = m.groups()[1]

		sendToIrc('<' + name + '> ' + text)

def ircToMinecraft():
	global infoCount, lock
	lines = follow(open(ircDir+ '/out'))
	regex = re.compile('\d+-\d+-\d+ \d+:\d+ <([^>]+)> ([^\s]*)(\s?)(.*)')
	for line in lines:
		m = regex.search(line)
		if not(m):
			continue
		name = m.groups()[0]
		cmd = m.groups()[1]
		sp = m.groups()[2]
		text = m.groups()[3]

		if name == 'minecraft':
			continue

		mc = open(mcDir + '/in', 'w')
		if cmd == 'playsound':
			mc.write('/playsound ' + text + '\n')
		elif cmd == 'list' and text == '':
			lock.acquire()
			infoCount += 3
			lock.release()
			mc.write('/list\n')
		else:
			mc.write('/say ' + name + ': ' + cmd + sp + text + '\n')
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
	
	ircToMinecraft()
