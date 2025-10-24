#!/bin/bash
sudo pacman -Syu
sudo pacman -S --noconfirm git python python-pip jre-openjdk jdk-openjdk rust
sudo useradd crafty -s /bin/bash
