#!/bin/bash

# Update the package repository index
sudo apt-get update

# Install the NGINX web server
sudo apt-get install nginx

# Install the necessary dependencies
sudo apt-get install build-essential libpcre3 libpcre3-dev libssl-dev unzip zlib1g-dev

# Download the NGINX RTMP module source code from the GitHub repository
cd /tmp
git clone https://github.com/arut/nginx-rtmp-module.git

# Download the NGINX source code
wget https://nginx.org/download/nginx-1.21.0.tar.gz
tar -zxvf nginx-1.21.0.tar.gz
cd nginx-1.21.0

# Configure NGINX with the RTMP module
./configure --with-http_ssl_module --add-module=/tmp/nginx-rtmp-module

# Compile and install NGINX
make
sudo make install

# Start NGINX
sudo systemctl start nginx

# Verify that NGINX is running
sudo systemctl status nginx
