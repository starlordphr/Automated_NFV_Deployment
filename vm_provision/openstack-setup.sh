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

# UI script dependencies
sudo apt-get install -y python-matplotlib

# Download and install python-openstackclient
print-highlight "----- Setting up openstack..."
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
chmod +x install-openstack.sh
sudo cp install-openstack.sh /opt/stack
sudo su - stack 	# will swtich user here

# call install-openstack.sh after switching user
