Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  # Allow access to Django app inside VM from localhost on its default port
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8001, host: 8001
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 3306, host: 3306

  # Ensure time inside vagrant VM stays sync'd for make builds
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
    v.customize [ "guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-interval", 10000]
    v.customize [ "guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-min-adjust", 100]
    v.customize [ "guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-on-restore", 1]
    v.customize [ "guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold", 10000]
  end

  VM_BOX_USER = "ubuntu"
  ODA_SOURCE_PATH  = "/home/#{VM_BOX_USER}/src/oda"
  ODA_INSTALL_PATH = "/home/#{VM_BOX_USER}/oda" 

  # Keep ODA sources in sync
  config.vm.synced_folder ".", ODA_SOURCE_PATH

  config.ssh.forward_agent = true

  config.vm.provision :ansible_local do |ansible|
    ansible.install_mode = "pip"
    ansible.version = "2.4.0.0"

    ansible.provisioning_path = ODA_SOURCE_PATH
    ansible.playbook = "ansible/site.yml"

    # Load external role requirements
    ansible.galaxy_role_file = "ansible/requirements.yml"
    ansible.galaxy_roles_path = "ansible/galaxy"

    # Uncomment to change ansible verbosity
    #ansible.verbose = "vvv"

    # Default host is a member of all groups
    ansible.groups = Hash[["db", "app", "web", "development"].map {|g| [g, ["default"]] }]

    # Ubuntu 16.04 only ships with Python3, so make ansible use it
    # so we don't need some boostrapping hacks to run Python 2.7
    ansible.host_vars = {
      "default" => {
        "ansible_python_interpreter" => "/usr/bin/python3"
      }
    }

    # Configure ansible install inside Vagrant VM environment
    ansible.extra_vars = {
      "oda_source_path"  => ODA_SOURCE_PATH,
      "oda_install_path" => ODA_INSTALL_PATH,

      "oda_user"  => VM_BOX_USER,
      "oda_group" => VM_BOX_USER,

      "mysql_users" => [
	"name"     => VM_BOX_USER,
	"password" => "{{ mysql_root_password }}",
	"priv"     => "{{ mysql_databases[0].name }}.*:ALL",
      ]
    }
  end
end
