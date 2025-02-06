#!/bin/bash
sudo dnf update -y
sudo dnf group install "Development tools" -y
sudo dnf install git python3 python3-devel java-17-openjdk-headless java-21-openjdk-headless  -y
sudo useradd crafty -s /bin/bash
