#!/bin/bash

# Tutorial for this setup:
# https://docs.openstack.org/keystone/latest/install/keystone-install-ubuntu.html

# import scripts
source ./utils.sh

# If any of the commands fails, exit the script
set -e
sudo apt-get update

# Install dependency MySQL
print-highlight "----- Installing MySQL..."
# User will need to set a root password when prompted
sudo apt-get install -y mysql-server
# And enter the password again when prompted
print-highlight "----- Please enter root user password when prompted"
mysql -u root -p < scripts/create_keystone.sql

# Install keystone and apache
print-highlight "----- Installing keystone and apache..."
sudo apt-get install -y keystone apache2 libapache2-mod-wsgi
# Modify keystone configuration
# TODO: maybe find a more robust way to do this...
print-highlight "----- Configuring keystone..."
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
print-highlight "----- Configuring the Apache HTTP server..."
sudo echo "ServerName controller" >> /etc/apache2/apache2.conf
# Finalize the installation
print-highlight "----- Restarting the Apache service..."
service apache2 restart

# Setting up a minimal set of environment variables for authentication
print-highlight "----- Openstack: Configuring authentication..."
echo "export OS_IDENTITY_API_VERSION=3" >> ~/.bashrc
#echo "export OS_AUTH_URL=http://localhost:5000/v3" >> ~/.bashrc
echo "export OS_AUTH_URL=http://controller:35357/v3" >> ~/.bashrc
echo "export OS_DEFAULT_DOMAIN=default" >> ~/.bashrc
echo "export OS_USERNAME=admin" >> ~/.bashrc
echo "export OS_PASSWORD=himitsu" >> ~/.bashrc
echo "export OS_PROJECT_NAME=admin" >> ~/.bashrc
echo "export OS_USER_DOMAIN_NAME=default" >> ~/.bashrc
echo "export OS_PROJECT_DOMAIN_NAME=default" >> ~/.bashrc
source ~/.bashrc
