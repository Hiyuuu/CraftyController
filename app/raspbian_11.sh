#!/bin/bash
echo "パッケージリストを更新しています..."
sudo apt update -y
echo "依存パッケージをインストールしています..."
sudo apt install git python3 python3-dev python3-pip python3-venv libcurl4 software-properties-common -y
install_return=$?
if [[ "$install_return" != 0 ]];then
	echo "パッケージのインストール中にエラーが発生しました。"
	exit $install_return
fi
echo "crafty ユーザーを作成しています..."
sudo useradd crafty -s /bin/bash
exit 0
