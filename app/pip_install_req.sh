#!/bin/bash
echo "Crafty のディレクトリに移動し、ブランチ $2 をチェックアウトしています..."
cd $1/crafty-4
git checkout $2

echo "仮想環境を有効化しています..."
source ../.venv/bin/activate

echo "必要な Python パッケージをインストールしています..."
pip3 install wheel
pip3 install setuptools
pip3 install setuptools-rust
pip3 install --no-cache-dir -r requirements.txt
echo "仮想環境を無効化しています..."
deactivate
