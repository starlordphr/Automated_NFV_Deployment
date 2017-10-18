#!/bin/bash

# If any of the commands fails, exit the script
set -e

# https://docs.openstack.org/keystone/latest/install/keystone-install-ubuntu.html
# Install dependency MySQL
echo "----- Installing MySQL..."
# User will need to set a root password when prompted
sudo apt-get install -y mysql-server
# And enter the password again when prompted
echo "----- Please enter root user password when prompted"
mysql -u root -p < scripts/create_keystone.sql

# Install keystone and apache
echo "----- Installing keystone and apache..."
sudo apt-get install -y keystone apache2 libapache2-mod-wsgi
# Modify keystone configuration
# TODO: maybe find a more robust way to do this...
echo "----- Configuring keystone..."
sudo cp scripts/keystone_modified.conf /etc/keystone/keystone.conf
# Populate the Identity service database
sudo su -s /bin/sh -c "keystone-manage db_sync" keystone
# Initialize Fernet key repositories
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
# Bootstrap the Identity service
keystone-manage bootstrap --bootstrap-password himitsu \
  --bootstrap-admin-url http://controller:35357/v3/ \
  --bootstrap-internal-url http://controller:5000/v3/ \
  --bootstrap-public-url http://controller:5000/v3/ \
  --bootstrap-region-id RegionOne

# Configure the Apache HTTP server
echo "----- Configuring the Apache HTTP server"
sudo echo "ServerName controller" >> /etc/apache2/apache2.conf
# Finalize the installation
echo "----- Restarting the Apache service"
service apache2 restart
# Setting up a minimal set of environment variables for authentication
export OS_IDENTITY_API_VERSION=3
#export OS_AUTH_URL=http://localhost:5000/v3
export OS_AUTH_URL=http://controller:35357/v3
export OS_DEFAULT_DOMAIN=default
export OS_USERNAME=admin
export OS_PASSWORD=himitsu
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_DOMAIN_NAME=default

# Download and install python-openstackclient
echo "----- Openstack: Downloading OpenStack client..."
sudo apt-get install -y python-openstackclient

# Test
openstack image list
