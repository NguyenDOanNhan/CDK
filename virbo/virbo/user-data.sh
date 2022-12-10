#!/bin/bash
apt update
apt install nginx -y
sudo apt install mysql-client -y
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16
systemctl restart nginx
systemctl enable nginx
service nginx start
mv /var/www/html/index.nginx-debian.html /var/www/html/index.nginx-debian.html.bak
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.nginx-debian.html
