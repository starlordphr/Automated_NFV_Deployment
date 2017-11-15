#!/bin/bash

# Tutorial:
# https://docs.openstack.org/install-guide/
# May just make use of DevStack to install stuff needed:
# https://docs.openstack.org/devstack/latest/

# If any of the commands fails, exit the script
source utils.sh

set -e

# Update Ubuntu
print-highlight "----- Updating apt & Upgrading..."
sudo apt-get update
sudo apt-get -y upgrade

# Download and install python-openstackclient
print-highlight "----- Setting up openstack..."
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
chmod +x install-openstack.sh
sudo cp install-openstack.sh /opt/stack
sudo su - stack 	# will swtich user here
# git clone https://git.openstack.org/openstack-dev/devstack
# mkdir .cache	# to prevent a common error
# cd devstack
# touch local.conf
# echo "[[local|localrc]]" >> local.conf
# echo "ADMIN_PASSWORD=secret" >> local.conf
# echo "DATABASE_PASSWORD=$ADMIN_PASSWORD" >> local.conf
# echo "RABBIT_PASSWORD=$ADMIN_PASSWORD" >> local.conf
# echo "SERVICE_PASSWORD=$ADMIN_PASSWORD" >> local.conf
# echo "HOST_IP=192.168.1.118"	# May not need this
# ./stack.sh
