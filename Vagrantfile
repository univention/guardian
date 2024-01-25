# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "debian/bookworm64"

  config.vm.network "forwarded_port", guest: 5173, host: 5173

  # Installs some required packages.
  config.vm.provision "shell", name: "SYSTEM SETUP", inline: <<-SHELL
    apt-get update
    apt-get install -y git python3-venv nodejs npm curl pipx
    npm install --global yarn
    curl -L https://github.com/open-policy-agent/opa/releases/download/v0.53.0/opa_linux_amd64_static -o /bin/opa
    curl -L https://github.com/StyraInc/regal/releases/download/v0.8.0/regal_Linux_x86_64 -o /bin/regal
    chmod +x /bin/regal
    chmod +x /bin/opa
  SHELL

  # Creates a virtual env and installs the python project with poetry
  config.vm.provision "shell", name: "PROJECT SETUP", privileged: false, inline: <<-SHELL
    pipx install pre-commit==3.6.0
    export PATH=$PATH:/home/vagrant/.local/bin
    cd /vagrant && pre-commit install
    cd /vagrant/management-ui && yarn install
    for project in "management-api" "authorization-api" "guardian-lib"
    do
      VENV_PATH="/home/vagrant/venvs/$project"
      python3.11 -m venv $VENV_PATH
      $VENV_PATH/bin/pip install -U pip setuptools
      $VENV_PATH/bin/pip install poetry==1.6.1
      . $VENV_PATH/bin/activate
      cd "/vagrant/$project"
      poetry install
      deactivate
    done
  SHELL

  if ENV["VAGRANT_PROVISION_SSH_KEY"]
    # Path to the ssh key you need for accessing Gitlab.
    GIT_SSH_PRIVATE_KEY_SOURCE = ENV["VAGRANT_GIT_SSH_PRIVATE_KEY_SOURCE"].to_s.empty? ? "%s/.ssh/id_rsa" % [ENV["HOME"].to_s] : ENV["VAGRANT_GIT_SSH_PRIVATE_KEY_SOURCE"].to_s
    # Set a value if the key should be copied to some other place than the source.
    GIT_SSH_PRIVATE_KEY_DESTINATION = ENV["VAGRANT_GIT_SSH_PRIVATE_KEY_DESTINATION"].to_s
    config.vm.provision "file", source: GIT_SSH_PRIVATE_KEY_SOURCE, destination: GIT_SSH_PRIVATE_KEY_DESTINATION.empty? ? GIT_SSH_PRIVATE_KEY_SOURCE : GIT_SSH_PRIVATE_KEY_DESTINATION
  end

  if ENV["VAGRANT_PROVISION_GIT_CONFIG"]
    config.vm.provision "file", source: "%s/.gitconfig" % [ENV["HOME"].to_s], destination: ".gitconfig"
  end

  if ENV["VAGRANT_PROVISION_SSH_CONFIG"]
    config.vm.provision "file", source: "%s/.ssh/config" % [ENV["HOME"].to_s], destination: ".ssh/config"
  end

  if File.exist?("./vagrant_custom_provisioning.sh")
    config.vm.provision "shell", name: "CUSTOM SCRIPT", privileged: false, path: "./vagrant_custom_provisioning.sh"
  end
end
