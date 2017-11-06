'''
Assuming setup is done, use this program to automate certain processes
and interact with user.
Usage:
$ sudo python ui.py
'''

import os, select, time
from utils import *

toshell_read, toshell_write = os.pipe()
fromshell_read, fromshell_write = os.pipe()
polling_pool = None

def main():
	global polling_pool
	
	pid = os.fork()
	if pid < 0:
		raise Exception("fork failed")

	if pid == 0:
		# child process
		print "Starting shell in child process..."
		cmd = ['/bin/bash']

		# redirects child bash's input to be given by 'toshell'
		# and redirects child bash's stdout and stderr to be read from 'fromshell'
		os.dup2(toshell_read, 0)
		# os.dup2(fromshell_write, 1)
		os.close(1)
		os.close(2)
		os.dup(fromshell_write)
		os.dup(fromshell_write)
		os.close(fromshell_write)

		os.execvp(cmd[0], cmd)
	else:
		# parent process
		polling_pool = select.poll()
		polling_pool.register(fromshell_read)
			#select.POLLIN | select.POLLERR | select.POLLHUP

	# wait for child process to start...
	time.sleep(0.5)

	demo()
	# init()
	# demo_parse_table()

	# while True:
	# 	user_input = raw_input()

def give_command(cmd):
	nbytes = os.write(toshell_write, '%s\n' % cmd)
	return nbytes

def init():
	cmd_seq = [
		'sudo su - stack',
		'cd devstack',
		'source openrc'
	]
	for cmd in cmd_seq:
		give_command(cmd)

def demo():
	demo_cmds = ['sudo su - stack', 'whoami', 'cd devstack', 'ls']
	for cmd in demo_cmds:
		give_command(cmd)
		has_output = False
		for fd, event in polling_pool.poll(100):
			has_output = True
			output = os.read(fd, 4096)
			print "Command '%s' gives output:" % cmd
			print output
		if not has_output:
			print "Command '%s' gives no output..." % cmd

def demo_parse_table():
	give_command('openstack flavor list')
	output = os.read(fromshell_read, 65536)
	print "Received output:"
	print output
	print "Parsed object:"
	print parse_openstack_table(output)

if __name__ == '__main__':
	main()
