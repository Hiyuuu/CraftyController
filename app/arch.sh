#!/bin/bash
echo "システムを更新しています..."
sudo pacman -Syu
echo "依存パッケージをインストールしています..."
sudo pacman -S --noconfirm git python python-pip jdk-openjdk rust
install_return=$?
if [[ "$install_return" != 0 ]];then
	echo "パッケージのインストール中にエラーが発生しました。"
	exit $install_return
fi
echo "crafty ユーザーを作成しています..."
sudo useradd crafty -s /bin/bash
exit 0
