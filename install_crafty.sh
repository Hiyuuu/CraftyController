#!/bin/bash
sudo -v
sudo_test="$?"
if [ "${sudo_test}" -eq 127 ];then
    echo "エラー: インストールには sudo が必要です。"
    fail=1
elif [ "${sudo_test}" -eq 1 ];then
    echo "申し訳ありません - お使いのシステムでは、ユーザーによる sudo コマンドの実行が制限されているようです。"
    fail=1
elif [ "${sudo_test}" -eq 0 ];then
    fail=0
else
    echo "深刻なエラーが発生しました (sudo_test は ${sudo_test} です)。このエラーを開発者に報告してください。"
fi

if [ "${fail}" -eq 1 ];then
    echo "詳細についてはドキュメントを参照してください:"
    echo "    https://wiki.craftycontrol.com/"
elif [ "${fail}" -eq 0 ];then
    if [[ $EUID -ne 0 ]]; then
        echo "注意: root ユーザーではありません。sudo を使用して root として再実行します。"
        sudo "$0"
    else
        echo "Craftyをインストールしています..."
        # Check to see what package manager to use.
        if [ -d "/etc/apt" ]; then
            sudo apt install python3-pip python3-distro -y
        elif [ -d "/etc/pacman.d" ]; then
            sudo pacman -S python-pip python-distro --noconfirm
        else
            sudo dnf install python3-pip python3-distro -y
        fi
        python3 install_crafty.py
    fi
else
    echo "深刻なエラーが発生しました (fail 値は ${fail} です)。このエラーを開発者に報告してください。"
fi
