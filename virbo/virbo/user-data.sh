#!/bin/bash
apt update
apt install nginx -y
systemctl restart nginx
systemctl enable nginx
service nginx start
mv /var/www/html/index.nginx-debian.html /var/www/html/index.nginx-debian.html.bak
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.nginx-debian.html