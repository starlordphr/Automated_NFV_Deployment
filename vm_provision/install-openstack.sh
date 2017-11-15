#!/bin/bash

sudo su - stack
git clone https://git.openstack.org/openstack-dev/devstack
mkdir .cache	# to prevent a common error
cd devstack
touch local.conf
echo "[[local|localrc]]" >> local.conf
echo "ADMIN_PASSWORD=secret" >> local.conf
echo "DATABASE_PASSWORD=$ADMIN_PASSWORD" >> local.conf
echo "RABBIT_PASSWORD=$ADMIN_PASSWORD" >> local.conf
echo "SERVICE_PASSWORD=$ADMIN_PASSWORD" >> local.conf
echo "HOST_IP=192.168.1.118"	# May not need this
./stack.sh
