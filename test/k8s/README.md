# How to run test
## Run with docker image
Docker command must be run inside the role director:
Example:
- home
  |___vagrant
      |___k8s => Docker command must be excute inside "k8s" directory
          |__default
          |__files
          |__handlers
          |__inventory
          |__meta
          |__molecule
          |__resources
          |__tasks
          |__templates
          |__vars
docker run --rm -it  -v "$(pwd)":/vagrant/$(basename "${PWD}") \
    -v /var/run/docker.sock:/var/run/docker.sock     \
    -w /vagrant/$(basename "${PWD}")     \
    quay.io/ansible/molecule:3.0.4   /bin/sh -c "pip install kubernetes; apk add sshpass; molecule test --all"

Role Name
=========

k8s: this role will set up kubernetes cluser and install istio with mTLS 

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
