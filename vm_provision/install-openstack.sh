#!/bin/bash

git clone https://git.openstack.org/openstack-dev/devstack
mkdir .cache	# to prevent a common error
cd devstack
touch local.conf
passwd=secret
echo "[[local|localrc]]" >> local.conf
echo "ADMIN_PASSWORD=$passwd" >> local.conf
echo "DATABASE_PASSWORD=$passwd" >> local.conf
echo "RABBIT_PASSWORD=$passwd" >> local.conf
echo "SERVICE_PASSWORD=$passwd" >> local.conf
echo "HOST_IP=192.168.1.118"	# May not need this
./stack.sh
