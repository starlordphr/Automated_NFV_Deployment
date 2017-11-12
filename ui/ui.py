'''
Assuming setup is done, use this program to automate certain processes
and interact with user.
Usage:
$ sudo python ui.py <args>
Arguments:

'''

import os, select, time, argparse, subprocess
import configs, utils

################
## child bash ##
################

BUF_SIZE = 65536

toshell_read, toshell_write = os.pipe()
fromshell_read, fromshell_write = os.pipe()
polling_pool = None

home_dir = ""

# TODO: maybe set up another thread for polling output??

#############
## console ##
#############

commands = {
	"help" : {
		"description" : "Show help message",
		"func_name" : "show_help"
	},
	"exit" : {
		"description" : "Exit console",
		"func_name" : "exit_console"
	},
	"conf" : {
		"description" : "Print current configuration (parsed to json format)",
		"func_name" : "show_config"
	},
	"demo" : {
		"description" : "Demonostrate parsing a table",
		"func_name" : "demo_parse_table"
	}
}
console_running = True
work_dir = ""

def main():
	global polling_pool

	# parse args
	args = parse_args()

	# process args to intialize configs module
	# will raise exception if input is ill-formatted
	configs.parse_sla_config(args.sla)
	
	# fork child bash
	pid = os.fork()
	if pid < 0:
		raise RuntimeError("fork failed")

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

	# first commands to child bash
	init()

	# process according to SLA specification
	print "Processing SLA configuration..."
	for vm in configs.sla_configs:
		cfg = configs.sla_configs[vm]
		configure_deployment(vm, cfg['vm_type'], cfg['deploy_config'])

	# user console
	while console_running:
		print '$',
		user_args = raw_input().split()

		if len(user_args) > 0:
			cmd = user_args[0]
			cmd_args = user_args[1:] if len(user_args) > 1 else []
			func = get_cmd_func(cmd)
			if func != None:
				func(cmd_args)

##############################
## child bash communication ##
##############################

def give_command(cmd):
	nbytes = os.write(toshell_write, '%s\n' % cmd)
	return nbytes

def poll_output(timeout=5000):
	for fd, event in polling_pool.poll(timeout):
		output = os.read(fd, BUF_SIZE)
		return output

	# TODO: add waitpid to see if child exits due to error

	return ""

def get_returncode():
	clear_historical_outputs()
	give_command("echo $?")
	output = poll_output(timeout=1000)
	return int(output)

# timeout will be at least how long we will have to wait
def poll_all_outputs(timeout=3000):
	has_output = True
	historical_output = ""
	while has_output:
		has_output = False
		output = poll_output(timeout)
		if len(output) > 0:
			has_output = True
			if len(historical_output) == 0:
				historical_output = output
			else:
				historical_output += "\n%s" % output
	return historical_output

# just swiftly poll all outputs
def clear_historical_outputs():
	# Assumes historical outputs are ready to send
	# on child's stdout or stderr
	return poll_all_outputs(100)

###########################
## console command funcs ##
###########################

def show_help(args=[]):
	for opt in commands:
		print "%-16s%s" % (opt, commands[opt]['description'])

def exit_console(args=[]):
	global console_running
	console_running = False
	# waitpid?

def show_config(args=[]):
	print utils.format_dict(configs.sla_configs)

###########################
## console backend funcs ##
###########################

def parse_args():
	# parse args
	parser = argparse.ArgumentParser()
	parser.add_argument('--sla', action='store', required=True,
		metavar='SLA_config_file', help='specify SLA config file')
	args = parser.parse_args()
	return args

def init():
	global home_dir
	print "Initialzing console..."

	# get working directory of THIS SCRIPT (do not confuse)
	work_dir = subprocess.check_output(['pwd']).strip()
	
	give_command('sudo su - stack')
	give_command('pwd')
	home_dir = poll_output(timeout=1000)
	if len(home_dir) == 0:
		print "[WARNING] Could not get home directory!"
	give_command('cd devstack')
	give_command('source openrc')    # may have output
	print poll_output(timeout=2000)

def get_cmd_func(cmd):
	if type(cmd) != str or cmd not in commands:
		print "%s: command not found" % cmd
		return None
	else:
		return globals().get(commands[cmd]['func_name'])

# returns None if given command doesn't return any output
def get_table(cmd, both=False):
	give_command(cmd)
	output = poll_output(timeout=7500)
	if both:
		return utils.parse_openstack_table(output), output
	else:
		return utils.parse_openstack_table(output)

##############################
## configuration automation ##
##############################

def configure_deployment(vm_name, vm_type, deploy_config):
	if vm_type == "server":
		# TODO: testing if the server already exists?
		create_server(vm_name, deploy_config)

def configure_oai():
	pass

def create_server(vm_name, deploy_config):
	# Step 1: Keypair
	if deploy_config["KEY_NAME"] == None:
		deploy_config["KEY_NAME"] = "%s_key" % deploy_config["INSTANCE_NAME"]
	
	# TODO: check if the user provides the path to its own key

	# check failed: create a new key
	give_command('ssh-keygen -q -N ""') # requires file name
	time.sleep(0.25)
	give_command('')	# use default
	time.sleep(0.25)
	rc = get_returncode()
	# TODO: check return code???
	give_command('openstack keypair create --public-key ~/.ssh/id_rsa.pub %s' % deploy_config["KEY_NAME"])
	print poll_output()

	# Step 2: Display keypair
	table, output = get_table('openstack keypair list', both=True)
	print output
	newkey = [entry for entry in table if entry['Name'] == deploy_config['KEY_NAME']][0]
	print "New key:"
	print utils.format_dict(newkey)

	if deploy_config["SECURITY_GROUP_NAME"] != None:
		# Step 3
		sec_grp = deploy_config['SECURITY_GROUP_NAME']
		print "Creating new security group: %s" % sec_grp
		
		give_command('openstack security group create %s' % sec_grp)
		give_command('openstack security group rule create --proto icmp %s' % sec_grp)
		give_command('openstack security group rule create --proto tcp --dst-port 22 %s' % sec_grp)
		
		print poll_all_outputs()
	else:
		# Step 4
		print "Using default security group"

		give_command('openstack security group rule create --proto icmp default')
		give_command('openstack security group rule create --proto tcp --dst-port 22 default')

		print poll_all_outputs()

		deploy_config['SECURITY_GROUP_NAME'] = 'default'

	# Step 5: Parse netID
	table, output = get_table('openstack network list', both=True)
	net_id = [entry for entry in table if entry['Name'] == deploy_config['NETWORK_NAME']][0]['ID']

	# Step 6: Create instance
	# TODO: what is the security group name when not specified?
	give_command('openstack server create --flavor %s --image %s --nic net-id=%s --security-group  --key-name %s %s' % (deploy_config['FLAVOR_NAME'],
		deploy_config['IMAGE_NAME'], net_id, deploy_config['SECURITY_GROUP_NAME'],
		deploy_config['KEY_NAME'], deploy_config['INSTANCE_NAME']))

##########################
## console debug & demo ##
##########################

def demo():
	demo_cmds = ['sudo su - stack', 'whoami', 'cd devstack', 'ls']
	for cmd in demo_cmds:
		give_command(cmd)
		has_output = False
		for fd, event in polling_pool.poll(100):
			has_output = True
			output = os.read(fd, BUF_SIZE)
			print "Command '%s' gives output:" % cmd
			print output
		if not has_output:
			print "Command '%s' gives no output..." % cmd

def demo_parse_table(args=[]):
	print "Command: openstack flavor list"
	print "Waiting for response..."
	give_command('openstack flavor list')
	output = os.read(fromshell_read, BUF_SIZE)
	print "Received output:"
	print output
	print "Parsed object:"
	print utils.parse_openstack_table(output)

##########
## main ##
##########

if __name__ == '__main__':
	main()
