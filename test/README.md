# Istio Keyfactor CA Integration Test

## Test Scenarios

- Single cluster with secret objects
- Single cluster with a secret in config template
- Multiple clusters with secret objects

### How to run

#### Prerequisites:

1.  **Operating System**: macOS or Linux(Ubuntu 16.04 above) (Currently, the integration test uses Ansible library as the driver to execute tests, and Ansible library can only be run in those OS that is mentioned above)
2.  **Vagrant**: Vagrant version 2.2.7 above
3.  **Istio**: Istio has a suitable version that is contained the Keyfactor CA agent

#### Steps to install prerequisites Softwares:

##### Vagrant:

     1. macOS:
    	Open terminal and follow steps below:
    	 - Install Homebrew
    	> /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    	 - Install Virtualbox cask
    	 > brew cask install virtualbox
    	 > brew cask install vagrant
    	  - Install vagrant plugins
    	 > vagrant plugin install vagrant-vbguest
    	 > vagrant plugin install vagrant-scp
     2. Linux (Ubuntu):
    	Open terminal and follow steps below:
    	 - Install Virtualbox
    	 > sudo apt-get install virtualbox
    	 > sudo apt-get install vagrant
    	  - Install vagrant plugins
    	 > vagrant plugin install vagrant-vbguest
    	 > vagrant plugin install vagrant-scp

#### Steps to run tests:

1.  Clone the example source code
2.  Update istioctl in the examples/release folder, the istioctl files must match with the list file names below: - istioctl-linux-amd64 (istioctl runable file for linux OS) - istioctl-osx (istioctl runable file for linux macOS) - istioctl-win.exe (istioctl runable file for Windows OS)
    ![Screenshot](/test/folder-tree.PNG)
3.  Update the root-cert.pem in the istio folder
    ![Screenshot](/test/root-cert.PNG)
4.  Change the terminal command to a test directory (the directory contains the Vagrantfile)
5.  Run the test with command below:

    Currently, the integration tests will be run when provisioning with command bellow:

    > vagrant up --provision

    Run test manually with command below:

    > vagrant ssh k8s-master-1 -c 'cd /vagrant/k8s && molecule test --all

![Screenshot](/test/run-test-1.PNG)
![Screenshot](/test/run-test-2.PNG)
