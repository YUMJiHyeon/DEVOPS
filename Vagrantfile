# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.insert_key = false
  config.vm.box = "digital_ocean"
  config.ssh.private_key_path = "/Users/yumjihyeon/.ssh/id_rsa"
  config.ssh.username = "root"
  config.vm.allowed_synced_folder_types = [:rsync] 
  config.vm.provision "shell", inline: <<-SHELL
    export DEBIAN_FRONTEND=noninteractive
    systemctl disable unattended-upgrades || true
    systemctl stop unattended-upgrades || true
    systemctl kill unattended-upgrades || true

    sed -i "s/#\\$nrconf{restart} = 'i';/\\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf 2>/dev/null || true

  SHELL

  config.vm.provider :digital_ocean do |provider|
    provider.token = ENV['DIGITAL_OCEAN_TOKEN']
    provider.ssh_key_name = "yumwlgus7@gmail.com"
    provider.image = "ubuntu-22-04-x64"
    provider.region = "ams3"
    provider.size = "s-1vcpu-1gb"
    provider.setup = false
  end

  config.vm.define "dbserver" do |db|
    db.vm.hostname = "dbserver"
    db.vm.synced_folder ".", "/vagrant", disabled: true
    db.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      until apt-get update -y; do sleep 5; done
      until apt-get install -y gnupg curl; do sleep 5; done
      curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
      echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list
      until apt-get update -y; do sleep 5; done
      until apt-get install -y mongodb-org; do sleep 5; done
      sed -i '/bindIp:/ s/127.0.0.1/0.0.0.0/' /etc/mongod.conf
      systemctl start mongod
      systemctl enable mongod
    SHELL
  end

  config.vm.define "webserver" do |web|
    web.vm.hostname = "webserver"
    web.vm.synced_folder ".", "/vagrant",
      type: "rsync",
      id: "vagrant-web-root",
      rsync__exclude: [".git/", "*.log", ".vagrant/"]
    web.vm.provider :digital_ocean do |do_os, override|
      override.vm.allowed_synced_folder_types = [:rsync]
    end
    web.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      pkill python3 || true
      until apt-get update -y; do sleep 5; done
      until apt-get install -y docker.io docker-compose; do sleep 5; done
      systemctl start docker
      systemctl enable docker
    SHELL
  end

  config.vm.define "secondary" do |sec|
    sec.vm.hostname = "secondary"
    sec.vm.synced_folder ".", "/vagrant",
      type: "rsync",
      id: "vagrant-sec-root",
      rsync__exclude: [".git/", "*.log", ".vagrant/"]
    sec.vm.provider :digital_ocean do |do_os, override|
      override.vm.allowed_synced_folder_types = [:rsync]
    end
    sec.vm.provision "shell", inline: <<-SHELL
      export DEBIAN_FRONTEND=noninteractive
      pkill python3 || true
      until apt-get update -y; do sleep 5; done
      until apt-get install -y docker.io docker-compose; do sleep 5; done
      systemctl start docker
      systemctl enable docker
    SHELL
  end
end