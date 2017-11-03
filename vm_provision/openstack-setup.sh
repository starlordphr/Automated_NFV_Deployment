#!/bin/bash

# Tutorial:
# https://docs.openstack.org/install-guide/
# May just make use of DevStack to install stuff needed:
# https://docs.openstack.org/devstack/latest/

# If any of the commands fails, exit the script
set -e

sudo apt update

# Download and install python-openstackclient
echo "----- Openstack: Downloading OpenStack client..."
sudo apt install -y software-properties-common
sudo add-apt-repository cloud-archive:pike
# Problem: keyring
# Solution: download from https://packages.ubuntu.com/xenial/all/ubuntu-cloud-keyring/download

sudo apt install -y python-openstackclient

# Test
openstack image list
