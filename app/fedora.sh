#!/bin/bash
sudo dnf update -y
sudo dnf group install "Development tools" -y
sudo dnf install git python3 python3-devel java-21-openjdk java-21-openjdk-devel libffi libffi-devel cargo -y
sudo useradd crafty -s /bin/bash
