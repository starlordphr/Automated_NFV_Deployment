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
		utils.print_highlight("====Deploying %s====" % vm)
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
		return output.strip()

	# TODO: add waitpid to see if child exits due to error

	return ""

def get_returncode():
	clear_historical_outputs()
	give_command("echo $?")
	output = poll_output(timeout=1000)
	if output.isdigit():
		return int(output)
	else:
		print "[WARNING] Return code not int: %s" % output
		return output

# timeout will be at least how long we will have to wait
def poll_all_outputs(timeout=5000, init_wait=2000):
	time.sleep(init_wait / 1000.0)

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
	return poll_all_outputs(timeout=200, init_wait=0)

def poll_all_quick_outputs():
	# Assumes only last command takes a long time
	output = poll_output()
	output = "%s\n%s" % (output, clear_historical_outputs())
	return output

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
		raise RuntimeError("[ERROR] Could not get home directory. Please restart and try again.")
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
	output = poll_output(-1)
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
	# create images folder
	img_dir = '%s/images' % home_dir
	utils.print_warning("Checking %s" % img_dir)
	if not os.path.isdir(img_dir):
		create_command = 'mkdir %s' % img_dir
		give_command(create_command)

	keystore_dir = '%s/keys' % home_dir
	if not os.path.isdir(keystore_dir):
		create_keystore_command = 'mkdir %s' % keystore_dir
		give_command(create_keystore_command)

	# check if image already exist
	give_command('openstack image show %s' % deploy_config['IMAGE_NAME'])
	output = poll_output(-1)
	utils.print_warning (output)
	if output == "Could not find resource %s" % deploy_config['IMAGE_NAME']:
		# Step 0: create image
		image_file = '%s/images/ubuntu-17.04.img' % home_dir
		if not os.path.isfile(image_file):
			rc = subprocess.call(['wget', '-O', image_file,
				'https://cloud-images.ubuntu.com/zesty/20171110/zesty-server-cloudimg-amd64.img'])
			# check return code: (may not be connected to internet)
		else:
			print "Image file: using exisiting file on disk: %s" % image_file

		cmd = 'openstack image create --unprotected --disk-format qcow2 --file %s %s' % (image_file,
			deploy_config['IMAGE_NAME'])
		print "Creating image... Please wait patiently:\n%s" % cmd
		give_command(cmd)
		print poll_output(-1) # will print image show
	elif output == "More than one resource exists with the name or ID '%s'" % deploy_config['IMAGE_NAME']:
		utils.print_warning("[WARNING] %s" % output)
	else:
		# image exists: don't re-create
		print "Using exisiting image '%s'" % deploy_config['IMAGE_NAME']

	# Step 1: Keypair
	if deploy_config["KEY_NAME"] == None or len(deploy_config["KEY_NAME"]) == 0:
		deploy_config["KEY_NAME"] = "%s_key" % deploy_config["INSTANCE_NAME"]

	# TODO: check if the user provides the path to its own key

	# check failed: create a new key
	give_command('rm -f ~/.ssh/id_rsa*')
	# output = poll_output(-1)
	time.sleep(0.25)
	give_command('ssh-keygen -q -N ""') # requires file name
	time.sleep(0.25)
	give_command('')	# use default
	time.sleep(0.25)
	# give_command('')	# possible overwrite
	print poll_all_outputs(timeout=3000, init_wait=0)
	# rc = get_returncode()
	# TODO: check return code???)
	# print "rc=%s" % rc 	# could be 1 if overwrite
	utils.print_warning("Creating keypair...")
	give_command('openstack keypair create --public-key ~/.ssh/id_rsa.pub %s' % deploy_config["KEY_NAME"])
	print poll_output(-1)

	# Copy the key to our keystore
	give_command('cp -f ~/.ssh/id_rsa %s/%s' % (keystore_dir, deploy_config["KEY_NAME"]))
	#give_command('chmod 400 %s/%s' % (keystore_dir, deploy_config["KEY_NAME"]))

	# Step 2: Display keypair
	table, output = get_table('openstack keypair list', both=True)
	print "Keypair list:"
	print output
	# This piece of code is creating a lot of errors
	#newkey = [entry for entry in table if entry['Name'] == deploy_config['KEY_NAME']][0]
	#print "New key:"
	#print utils.format_dict(newkey)

	if deploy_config["SECURITY_GROUP_NAME"] != None:
		# Step 3
		sec_grp = deploy_config['SECURITY_GROUP_NAME']
		print "Creating new security group: %s" % sec_grp

		give_command('openstack security group create %s' % sec_grp)
		print poll_output(-1)
		give_command('openstack security group rule create --proto icmp %s' % sec_grp)
		print poll_output(-1)
		give_command('openstack security group rule create --proto tcp --dst-port 22 %s' % sec_grp)
		print poll_output(-1)

		# print poll_all_outputs()
	else:
		# Step 4
		print "Using default security group"

		give_command('openstack security group rule create --proto icmp default')
		print poll_output(-1)
		give_command('openstack security group rule create --proto tcp --dst-port 22 default')
		print poll_output(-1)

		# print poll_all_outputs()

		deploy_config['SECURITY_GROUP_NAME'] = 'default'

	# Step 5: Parse netID
	table, output = get_table('openstack network list', both=True)
	net_id = [entry for entry in table if entry['Name'] == deploy_config['PRIVATE_NETWORK_NAME']][0]['ID']

	# Step 6: Create instance
	# check if server exists already
	give_command('openstack server show %s' % deploy_config['INSTANCE_NAME'])
	output = poll_output(-1)
	if output == "No server with a name or ID of '%s' exists." % deploy_config['INSTANCE_NAME']:
		print output
		cmd = 'openstack server create --flavor %s --image %s --nic net-id=%s --security-group %s --key-name %s %s' % (deploy_config['FLAVOR_NAME'],
			deploy_config['IMAGE_NAME'], net_id, deploy_config['SECURITY_GROUP_NAME'],
			deploy_config['KEY_NAME'], deploy_config['INSTANCE_NAME'])
		print "Creating server w/ command:"
		print cmd
		give_command(cmd)
		print poll_output(-1)
		#print poll_all_outputs(init_wait=10000) #My addition
	elif output == "More than one server exists with the name '%s'" % deploy_config['INSTANCE_NAME']:
		print "[WARNING] %s" % output
	else:
		# server exists: don't re-create
		print "Using exisiting server %s" % deploy_config['INSTANCE_NAME']

	#Creating floating ip
	time.sleep(20) # added to give time for the spawning to complete

	give_command('openstack floating ip create %s' % deploy_config['PUBLIC_NETWORK_NAME'])
	output = poll_output(-1)
	print output
	time.sleep(30)
	table = utils.parse_openstack_table(output)
	ip = [entry['Value'] for entry in table if entry['Field'] == 'floating_ip_address'][0]
	give_command('openstack server add floating ip %s %s' % (deploy_config['INSTANCE_NAME'], ip))
	#print poll_output()
	time.sleep(120)

	command_to_run = 'echo "hello world" > proof.txt'
	ssh_command = 'sudo ssh -T -oStrictHostKeyChecking=no -i %s/%s ubuntu@%s \'%s\'' % (keystore_dir, deploy_config["KEY_NAME"], ip, command_to_run)
	print ssh_command
	give_command(ssh_command)
	print poll_all_outputs()
	#give_command('echo "hello world" > proof.txt')	# to be replaced by OAI config
	#print poll_output(timeout=1000)
	#give_command('exit')
	#print poll_output()

	# To remove the key from known host
	# ssh-keygen -f "/root/.ssh/known_hosts" -R 172.24.4.6
	# sudo rm "/opt/stack/.ssh/known_hosts"

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
