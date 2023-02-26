#!/bin/bash
sudo dnf update -y
sudo dnf group install "Development tools" -y
sudo dnf install git python3 python3-devel python3-virtualenv java-16-openjdk java-16-openjdk-devel libffi libffi-devel -y
sudo useradd crafty -s /bin/bash
