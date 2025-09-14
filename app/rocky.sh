#!/bin/bash
sudo dnf update -y
sudo dnf install git-core python3 java-17-openjdk-headless -y
sudo useradd crafty -s /bin/bash
