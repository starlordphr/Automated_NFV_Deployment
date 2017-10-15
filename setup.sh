# Install VirtualBox
echo "----- Basic Setup: Installing VirtualBox..."
sudo apt-get -y install virtualbox

# Install Vagrant
echo "----- Basic Setup: Installing Vagrant..."
sudo apt-get -y install vagrant

# Download ubuntu 17.04 for virtual box
echo "----- Basic Setup: Downloading Ubuntu 17.04 box..."
vagrant box add bento/ubuntu-17.04 --provider virtualbox

# To list the newly downloaded box
echo "----- Basic Setup: Listing all the downloaded box..."
vagrant box list

# To start the ubuntu box
echo "----- Basic Setup: Starting ubuntu box..."
vagrant up
