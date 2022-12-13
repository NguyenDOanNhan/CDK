#!/bin/bash
apt-get update && upgrade -y
apt-get install -y nginx mysql-client nodejs npm
apt-get update
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
source ~/.bashrc
nvm install v16.17.1
