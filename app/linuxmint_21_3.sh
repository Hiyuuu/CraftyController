#!/bin/bash
sudo apt update -y
sudo apt install git python3 python3-dev python3-pip python3-venv libcurl4 software-properties-common openjdk-8-jdk-headless openjdk-8-jre-headless openjdk-11-jdk-headless openjdk-11-jre-headless openjdk-17-jdk-headless openjdk-17-jre-headless -y
sudo useradd crafty -s /bin/bash
