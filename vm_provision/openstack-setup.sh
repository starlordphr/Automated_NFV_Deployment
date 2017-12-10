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
print-highlight "We will now switch to stack user. You must install openstack \
as this user. Please execute the 'install-openstack.sh' script in the user's \
home directory."
sudo su - stack 	# will swtich user here
#sudo -u stack -H sh -c "sudo ./install-openstack.sh" # this doesn't work...
