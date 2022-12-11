#!/bin/bash
cat <<EOF > start.sh
#!/bin/bash
cd ~
apt-get update && upgrade -y
apt-get install -y nginx mysql-client
systemctl restart nginx
systemctl enable nginx
service nginx start
mv /var/www/html/index.nginx-debian.html /var/www/html/index.nginx-debian.html.bak
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.nginx-debian.html
EOF
bash start.sh