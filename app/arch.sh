#!/bin/bash
sudo pacman -Syu
sudo pacman -S --noconfirm git python python-pip jre-openjdk jdk-openjdk
sudo useradd crafty -s /usr/sbin/nologin
