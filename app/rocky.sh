#!/bin/bash
echo "パッケージリストを更新しています..."
sudo dnf update -y
echo "依存パッケージをインストールしています..."
sudo dnf install git-core python3 java-17-openjdk-headless -y
install_return=$?
if [[ "$install_return" != 0 ]];then
	echo "パッケージのインストール中にエラーが発生しました。"
	exit $install_return
fi
echo "crafty ユーザーを作成しています..."
sudo useradd crafty -s /bin/bash
exit 0
