#!/bin/bash
echo "パッケージリストを更新しています..."
sudo dnf update -y
echo "開発ツールをインストールしています..."
sudo dnf group install "Development tools" -y
echo "依存パッケージをインストールしています..."
sudo dnf install git python3 python3-devel java-17-openjdk java-17-openjdk-devel -y
install_return=$?
if [[ "$install_return" != 0 ]];then
	echo "パッケージのインストール中にエラーが発生しました。"
	exit $install_return
fi
echo "crafty ユーザーを作成しています..."
sudo useradd crafty -s /bin/bash
exit 0
