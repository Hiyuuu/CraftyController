#!/bin/bash
sudo apt update -y
sudo apt install wget apt-transport-https git python3 python3-dev  python3-pip python3-venv libcurl4 software-properties-common openjdk-11-jdk-headless openjdk-11-jre-headless openjdk-17-jdk-headless openjdk-17-jre-headless build-essential musl-dev libffi-dev rustc libssl-dev -y

# Install Temurin 8 (Formerly AdoptOpenJDK)- OpenJDK 8 is not in official repos as of Debian 11
wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | sudo tee /usr/share/keyrings/adoptium.asc
echo "deb [signed-by=/usr/share/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | sudo tee /etc/apt/sources.list.d/adoptium.list
sudo apt update -y
sudo apt install temurin-8-jdk -y

sudo useradd crafty -s /usr/sbin/nologin
