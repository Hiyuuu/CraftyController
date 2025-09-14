#!/bin/bash
sudo apt update -y
sudo apt install wget apt-transport-https git python3 python3-dev python3-pip python3-venv libcurl4 software-properties-common openjdk-17-jdk-headless openjdk-17-jre-headless build-essential musl-dev libffi-dev rustc libssl-dev -y

sudo useradd crafty -s /bin/bash
