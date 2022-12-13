#!/bin/bash
apt-get update && upgrade -y
apt-get install -y nginx mysql-client nodejs unzip npm
apt-get update
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
apt install unzip -y
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
source ~/.bashrc
nvm install v16.17.1
npm install pm2 -g
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=128M count=16
sudo /sbin/mkswap /var/swap.1
sudo chmod 600 /var/swap.1
sudo /sbin/swapon /var/swap.1
sudo swapon -s
echo '/var/swap.1   swap    swap    defaults        0   0' >> /etc/fstab
