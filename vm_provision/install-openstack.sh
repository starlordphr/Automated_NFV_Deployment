#!/bin/bash

source utils.sh

printf "\033[1;37m(Note: if you have set up MySQL before, please set the default password to be your MySQL's root password)\033[0m\n" # print in gray
echo -n "Please specify a default password for all services: "
read -s passwd
echo
echo -n "Confirm password: "
read -s passwd_r
echo

if [[ $passwd != $passwd_r ]]; then
	echo "Password confirmation failed!"
	exit 1
fi

git clone https://git.openstack.org/openstack-dev/devstack
mkdir .cache	# to prevent a common error
cd devstack
touch local.conf
#passwd=uclawing
echo "[[local|localrc]]" >> local.conf
echo "ADMIN_PASSWORD=$passwd" >> local.conf
echo "DATABASE_PASSWORD=$passwd" >> local.conf
echo "RABBIT_PASSWORD=$passwd" >> local.conf
echo "SERVICE_PASSWORD=$passwd" >> local.conf
#echo "HOST_IP=192.168.1.118" >> local.conf  # no need for this
