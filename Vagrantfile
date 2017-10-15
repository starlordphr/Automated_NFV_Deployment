Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-17.04"
  config.vm.provision :shell, :path => "vm_provision/provision-ubuntu-17.04.sh"
  config.vm.network "private_network", ip: "10.0.0.10"

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50", "--cpus", "4"]
    vb.memory = 6144
  end
end
