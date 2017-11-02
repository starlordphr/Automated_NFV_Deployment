#!/bin/bash

# Tutorial for this setup:
# https://docs.openstack.org/glance/pike/install/install-ubuntu.html

# import scripts
source ./utils.sh

# Check if required programs exist
testcmds mysql openstack

set -e
sudo apt-get update

###################
## Prerequisites ##
###################

# mysql ???

#. admin-openrc	#???

# Create the glance user
openstack user create --domain default --password-prompt glance
# Add the admin role to the glance user and service project
openstack role add --project service --user glance admin
# Create the glance service entity
openstack service create --name glance \
--description "OpenStack Image" image
# Create the Image service API endpoints
openstack endpoint create --region RegionOne \
image public http://controller:9292
openstack endpoint create --region RegionOne \
image internal http://controller:9292
openstack endpoint create --region RegionOne \
image admin http://controller:9292

######################################
## Install and configure components ##
######################################


