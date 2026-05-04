#!/usr/bin/env python3

import argparse
import json
import logging
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import time

import distro as pydistro

from app.helper import helper
from app.pretty import pretty
from app.java_manager import java_manager

with open("config.json", "r", encoding="utf-8") as config_file:
    defaults = json.load(config_file)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--debug", help="デバッグモードを有効にする", default=False, action="store_true"
)
parser.add_argument(
    "-s", "--ssh", help="GitをSSHモードで実行する", default=False, action="store_true"
)

logging.basicConfig(
    filename="installer.log",
    filemode="w",
    format="[+] Crafty インストーラー: %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

args = parser.parse_args()

if args.debug:
    defaults["debug_mode"] = True
if defaults["debug_mode"]:
    logger.setLevel(logging.DEBUG)
    pretty.info("デバッグモードが有効になりました")
    logger.info("デバッグモードが有効になりました")

if args.ssh:
    defaults["clone_method"] = "ssh"
    pretty.info("SSHを使用してGitクローンを試行します")
    logger.info("SSHを使用してGitクローンを試行します")


# ヘッダー表示
def do_header():
    time.sleep(2)

    if not defaults["debug_mode"]:
        helper.clear_screen()

    msg = "-" * 25
    msg += "# \t \t Crafty Controller 4.0 Linux インストーラー \t \t #"
    msg += "-" * 25
    msg += "\n \t\t\t このプログラムは、お使いのLinuxマシンにCrafty Controller 4.0をインストールします"
    msg += "\n \t\t\t このプログラムは完璧ではありませんが、セットアップを完了するために最善を尽くします"

    msg += "\n"
    pretty.header(msg)


# 他のディストリビューション用のシェルスクリプトをここで定義してサポートを強化できます
def do_distro_install(target_distro):
    real_dir = os.path.abspath(os.curdir)

    pretty.warning(
        "お使いのシステムの状況によっては、このインストールに時間がかかる場合があります。"
    )
    pretty.warning(
        "インストールが完了するまでお待ちください。途中で終了するとシステムが破損する恐れがあります。"
    )

    pretty.info("python3 と pip を更新しています")
    script = os.path.join(real_dir, "app", target_distro)

    logger.info("%s を実行しています", script)

    try:
        # スクリプトに実行権限があることを確認します。
        os.chmod(script, 0o0775)
        p = subprocess.Popen(script, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            sys.stdout.write(line.decode("utf-8"))
        rc = p.wait()
        if rc != 0:

            raise RuntimeError(f"スクリプトがコード {rc} で終了しました")

    except Exception as e:
        pretty.critical(f"依存関係のインストール中にエラーが発生しました: {e}")
        logger.exception("依存関係のインストール中にエラーが発生しました: %s", exc_info=e)
        sys.exit(1)


# Javaのインストール管理
def do_java_install(install_dir: pathlib.Path):
    pretty.info("Javaのセットアップを確認しています")
    
    if defaults["unattended"]:
        return None

    use_custom_java = helper.get_user_yesno(
        "特定のバージョンのJavaを個別にダウンロードしてインストールしますか？（システムのJavaを使用する場合は 'n'）",
        timeout=30,
        default=False
    )

    if use_custom_java:
        version = helper.get_user_valid_input(
            "どのバージョンのJavaをインストールしますか？",
            ["8", "11", "17", "21"],
            timeout=30,
            default="17"
        )
        java_path = java_manager.download_java(version, install_dir)
        if java_path:
            pretty.info(f"Java {version} が {java_path} にインストールされました。")
            return java_path
    
    return None


# 仮想環境（venv）を作成し、Gitリポジトリをクローンします
def setup_repo(target_directory: pathlib.Path):
    do_header()

    # 新しい仮想環境を作成
    pretty.info("新しい仮想環境（venv）を作成しています")

    venv_dir = pathlib.Path(target_directory, ".venv")

    # インストールディレクトリに移動
    os.chdir(target_directory)
    pretty.info(f"インストールディレクトリに移動します: {os.path.abspath(os.curdir)}")
    logger.info("ディレクトリを %s に変更しました", os.path.abspath(os.curdir))

    # 仮想環境を作成中
    try:
        subprocess.check_output([sys.executable, "-m", "venv", venv_dir], text=True)
    except subprocess.CalledProcessError as e:
        pretty.critical(
            "仮想環境を作成できませんでした - venvの作成に失敗しました（ログを確認してください）"
        )
        logger.critical(
            "venvサブプロセスが異常終了しました（コード: %i）。出力:\n%s",
            e.returncode,
            e.output,
        )
        helper.cleanup_bad_install(target_directory)
        sys.exit(1)
    except Exception as e:
        pretty.critical(f"仮想環境を作成できませんでした - {e}")
        logger.exception("仮想環境を作成できませんでした！", exc_info=e)
        helper.cleanup_bad_install(target_directory)
        sys.exit(1)

    clone_method = defaults["clone_method"]

    # リポジトリをクローン中
    pretty.info("Gitリポジトリをクローンしています... これには数分かかる場合があります")
    if clone_method == "ssh":
        clone_repo_ssh(target_directory)
    else:
        clone_repo_https(target_directory)


def confirm_ssh_key_location(key_location, tries=0):
    pretty.info(f"試行回数: {tries}")
    if key_location is None:
        key_location = helper.get_user_open_input(
            "SSHキーを検出できませんでした - SSHキーのフルパスを入力するか、'https' と入力してHTTPSにフォールバックしてください"
        )

    if key_location == "https" or tries > 2:
        pretty.info("HTTPSにフォールバックします")
        return "https"

    if not helper.check_file_exists(key_location):
        pretty.warning("指定されたキーが存在しません！")
        return confirm_ssh_key_location(None, tries + 1)

    key_confirm = helper.get_user_valid_input(
        f"{key_location} からSSHキーが選択されました。このキーを使用しますか？",
        ["y", "n"],
    )

    if key_confirm == "y":
        return key_location
    else:
        key_location = helper.get_user_open_input(
            "使用したいSSHキーのフルパスを指定してください"
        )
        return confirm_ssh_key_location(key_location, tries + 1)


def clone_repo_ssh(target_directory: pathlib.Path):
    invoking_user = os.getenv("SUDO_USER", "root")
    user_ssh_dir = f"/home/{invoking_user}/.ssh/"
    if helper.check_file_exists(user_ssh_dir + "id_ed25519"):
        ssh_key_loc = confirm_ssh_key_location(user_ssh_dir + "id_ed25519")
    elif helper.check_file_exists(user_ssh_dir + "id_rsa"):
        ssh_key_loc = confirm_ssh_key_location(user_ssh_dir + "id_rsa")
    else:
        ssh_key_loc = confirm_ssh_key_location(None)

    if ssh_key_loc == "https":
        return clone_repo_https(target_directory)

    try:
        embed_ssh_command = "ssh -i '{ssh_key_loc}'"
        subprocess.check_output(
            [
                "git",
                "clone",
                "git@gitlab.com:crafty-controller/crafty-4.git",
                "--config",
                f'core.sshCommand="{embed_ssh_command}"',
            ],
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.critical(
            "git clone が異常終了しました（コード: %i）。出力:\n%s",
            e.returncode,
            e.output,
        )
        logger.critical("Gitクローンに失敗しました！正しいキーを指定しましたか？")
        pretty.critical("クローンに失敗しました。HTTPSにフォールバックします。")
        clone_repo_https(target_directory)
    except Exception as e:
        logger.exception("エラー: %s", exc_info=e)
        helper.cleanup_bad_install(target_directory)
        sys.exit(1)


def clone_repo_https(target_directory: pathlib.Path):
    try:
        subprocess.check_output(
            ["git", "clone", "https://gitlab.com/crafty-controller/crafty-4.git"]
        )
    except Exception as e:
        logger.critical("Gitクローンに失敗しました！")
        logger.exception("エラー:", exc_info=e)
        pretty.critical("クローンできませんでした。詳細は installer.log を確認してください！")
        pretty.warning("不完全なインストールをクリーンアップして終了します...")
        helper.cleanup_bad_install(target_directory)
        sys.exit(1)


# 選択したブランチに切り替え、pipインストールなどを実行します
def do_virt_dir_install(
    starting_directory: pathlib.Path, target_directory: pathlib.Path
):
    do_header()

    # 運命の選択（ブランチ選択）
    pretty.info("インストールするブランチを選択してください:")
    pretty.info("Craftyには複数のブランチがあります:")
    pretty.info("Master - 比較的安定していますが、いくつかのバグが残っている可能性があります")
    pretty.info("Dev    - 非常に不安定です。バグが多く、新機能がテストされています")

    # 自動実行（アンアテンデッド）モード
    # ブランチの選択
    if not defaults["unattended"]:
        branch = helper.get_user_valid_input(
            "Craftyのどのブランチを実行しますか？", ["master", "dev"], timeout=30, default="master"
        )

    else:
        branch = defaults["branch"]

    crafty_directory = pathlib.Path(target_directory, "crafty-4").resolve()
    # gitリポジトリディレクトリに移動
    pretty.info(f"リポジトリディレクトリに移動します: {crafty_directory}")
    logger.info("ディレクトリを %s に変更しました", crafty_directory)
    os.chdir(crafty_directory)

    logger.info("ユーザーが %s ブランチを選択しました", branch)

    # ブランチ選択
    if branch == "master":
        pretty.info("安定版（Master）を選択しました")

    elif branch == "dev":
        pretty.info("開発版（Dev）を選択しました。幸運を！")

    # クイックスクリプト作成 / pipインストール実行
    do_pip_install(branch, starting_directory, target_directory)


# シェルスクリプト経由でpipの要件をインストール
def do_pip_install(
    branch: str, starting_directory: pathlib.Path, target_directory: pathlib.Path
):
    os.chmod(pathlib.Path(starting_directory, "app", "pip_install_req.sh"), 0o0775)
    pip_install_script_src = pathlib.Path(
        starting_directory, "app", "pip_install_req.sh"
    )
    pip_install_script_dst = pathlib.Path(target_directory, "pip_install_req.sh")

    logger.info("PIPインストールスクリプトをコピーしています")
    shutil.copyfile(pip_install_script_src, pip_install_script_dst)

    pip_command = [pip_install_script_dst, target_directory, branch]

    logger.info("ファイル %s に実行権限を付与しています", pip_install_script_dst)
    helper.chmod_add_exec(pip_install_script_dst)

    logger.info("Pipを実行しています: %s", pip_command)
    pretty.warning(
        "Crafty用のPythonモジュールをインストールします - インターネット接続速度によっては、この処理に時間がかかる場合があります"
    )

    time.sleep(3)

    try:
        p = subprocess.Popen(pip_command, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            sys.stdout.write(line.decode("utf-8"))
        rc = p.wait()
        if rc != 0:

            raise RuntimeError(f"異常な終了コード {rc}")

    except Exception as e:
        logger.error("エラーによりPipが失敗しました: %s", e)
        sys.exit(1)

    if not defaults["debug_mode"]:
        os.remove(pip_install_script_dst)


# run_crafty.sh を作成
def make_startup_script(target_directory: pathlib.Path):
    os.chdir(target_directory)
    logger.info("%s に移動しています", os.path.abspath(os.curdir))

    txt = "#!/bin/bash\n"
    txt += f"cd {target_directory}\n"
    txt += "source .venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += f"exec python{sys.version_info.major} main.py \n"
    with open("run_crafty.sh", "w", encoding="utf-8") as run_crafty_sh_file:
        run_crafty_sh_file.write(txt)
        run_crafty_sh_file.close()
    helper.chmod_add_exec(pathlib.Path("run_crafty.sh"))


# update_crafty.sh を作成
def make_update_script(target_directory: pathlib.Path):
    os.chdir(target_directory)
    logger.info("%s に移動しています", os.path.abspath(os.curdir))

    txt = "#!/bin/bash\n"
    txt += f"cd {target_directory}\n"
    txt += "source .venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += "\n"
    txt += "if [[ -v 1 ]]; then\n"
    txt += '    yn="$1"\n'
    txt += "fi\n"
    txt += "\n"
    txt += "while true; do\n"
    txt += "    if [[ ! -v yn ]]; then\n"
    txt += "        read -t 30 -p 'ローカルの変更をすべて上書きしてもよろしいですか？ (30秒で自動的に Y) [Y/N]: ' yn\n"
    txt += "        if [ $? -gt 128 ]; then yn='y'; echo 'y'; fi\n"
    txt += "    fi\n"
    txt += "    \n"
    txt += "    case ${yn:-y} in\n"
    txt += "        [yY] | -y )\n"
    txt += "            git reset --hard origin/master\n"
    txt += "            break;;\n"
    txt += "        [nN] | -n )\n"
    txt += "            break;;\n"
    txt += "        * )\n"
    txt += "            unset yn\n"
    txt += "            echo 'Y または N で答えてください。';;\n"
    txt += "    esac\n"
    txt += "done\n"
    txt += "\n"
    txt += "git pull \n"
    txt += "python3 -m ensurepip --upgrade \n"
    txt += "pip3 install --upgrade pip --no-cache-dir\n"
    txt += "pip3 install -r requirements.txt --no-cache-dir \n"
    with open("update_crafty.sh", "w", encoding="utf-8") as update_crafty_sh_file:
        update_crafty_sh_file.write(txt)
        update_crafty_sh_file.close()

    helper.chmod_add_exec(pathlib.Path("update_crafty.sh"))


# サービスとして実行するための run_crafty_service.sh を作成
def make_service_script(target_directory: pathlib.Path):
    os.chdir(target_directory)
    logger.info("%s に移動しています", os.path.abspath(os.curdir))

    txt = "#!/bin/bash\n"
    txt += f"cd {target_directory}\n"
    txt += "source .venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += f"python{sys.version_info.major} main.py -d\n"
    with open(
        "run_crafty_service.sh", "w", encoding="utf-8"
    ) as run_crafty_service_file:
        run_crafty_service_file.write(txt)
        run_crafty_service_file.close()

    helper.chmod_add_exec(pathlib.Path("run_crafty_service.sh"))


def make_service_file(target_directory: pathlib.Path):
    os.chdir(target_directory)
    logger.info("%s に移動しています", os.path.abspath(os.curdir))
    txt = f"""
[Unit]
Description=Crafty 4
After=network.target

[Service]
Type=simple

User=crafty
WorkingDirectory={target_directory}

ExecStart=/usr/bin/bash {target_directory}/run_crafty_service.sh

Restart=on-failure
# その他の再起動オプション: always, on-abort など

# install セクションは起動時に
# `systemctl enable` を使用するために必要です
# 自動的に有効化して開始したいユーザーサービスの場合は、
# `default.target` を使用してください
# システムレベルのサービスの場合は、`multi-user.target` を使用してください
[Install]
WantedBy=multi-user.target
"""

    with open("crafty.service", "w", encoding="utf-8") as crafty_service_file:
        crafty_service_file.write(txt)
        crafty_service_file.close()

    shutil.copy2(
        pathlib.Path(target_directory, "crafty.service"), "/etc/systemd/system/"
    )


# ディストリビューションを取得
def get_distro():
    distro_id = pydistro.id()
    version = pydistro.version()
    with open("linux_versions.json", "r", encoding="utf-8") as linux_versions_file:
        linux_versions = json.load(linux_versions_file)
    sys.stdout.write(f"検出されたOS: {distro_id} - バージョン: {version}\n")

    distro_file = None

    if distro_id == "arch" or distro_id == "archarm" or distro_id == "manjaro":
        logger.info("%s バージョン %s を検出しました", distro_id, version)
        return "arch.sh"

    current_distro = distro_id
    user_version = str(version).replace(".", "_")
    if current_distro not in linux_versions:
        # サポートされていないディストリビューションの場合
        distros = linux_versions.keys()
        logger.critical("サポートされていないディストリビューションです。以下のみをサポートしています: %s", distros)
        return
    if version not in linux_versions[current_distro]["versions"]:
        # サポートされていないディストリビューションのバージョンの場合
        versions = linux_versions[current_distro]["versions"]
        logger.critical(
            "サポートされていないバージョンです。%s は以下のみをサポートしています: %s", current_distro, versions
        )
        return

    logger.info("%s %s を検出しました！", current_distro, user_version)

    if helper.check_file_exists(
        os.path.join("app", f"{current_distro}_{user_version}.sh")
    ):
        distro_file = f"{current_distro}_{user_version}.sh"
    elif helper.check_file_exists(os.path.join("app", f"{current_distro}.sh")):
        distro_file = f"{current_distro}.sh"
    if distro_file is None:
        logger.critical(
            "ディストリビューションを特定できません: ID:%s - バージョン:%s", distro_id, version
        )
        logger.debug("ファイル: %s", distro_file)
    return distro_file


if __name__ == "__main__":
    logger.info("インストーラーを開始しました")

    starting_dir = pathlib.Path(os.path.curdir).resolve()
    temp_dir = pathlib.Path(starting_dir, "temp")

    do_header()

    # Linuxかどうかを確認
    if platform.system() != "Linux":
        pretty.critical("このスクリプトは Linux 専用です")
        logger.critical("このスクリプトにはLinuxが必要です")
        sys.exit(1)

    pretty.info("Linuxチェック完了")
    pretty.info(
        f"Pythonバージョン確認 - {sys.version_info.major}.{sys.version_info.minor}"
    )

    user_distro = get_distro()
    if not user_distro:
        pretty.critical("お使いのディストリビューションはサポートされていません。")
        logger.critical("ディストリビューション情報が見つかりません")
        sys.exit(1)

    # デフォルトのPythonチェック
    py_check = False

    # Python 3.9 以上かどうかを確認
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 9):
        pretty.critical("このスクリプトには Python 3.9 以上が必要です！")
        pretty.critical(
            f"現在のバージョンは Python {sys.version_info.major}.{sys.version_info.minor} です。"
        )
        logger.critical(
            "Python バージョンが 3.9 未満です: %i.%i が見つかりました",
            sys.version_info.major,
            sys.version_info.minor,
        )
        time.sleep(1)
        pretty.warning(
            "Pythonのバージョンが要件を満たしていません。こちらで修正（インストール）しますか？"
        )
    else:
        py_check = True

    # 自動実行（アンアテンデッド）モード
    if not defaults["unattended"]:
        install_requirements = helper.get_user_valid_input(
            f"{user_distro} の要件をインストールしますか？", ["y", "n"], timeout=30, default="y"
        )
    else:
        install_requirements = "y"

    if install_requirements == "y":
        pretty.info(
            f"{user_distro} に必要なパッケージをインストールします。プロンプトが表示されたら sudo パスワードを入力してください。"
        )
        do_distro_install(user_distro)
    else:
        if not py_check:
            pretty.critical("このスクリプトには Python 3.9 以上が必要です！")
            helper.cleanup_bad_install()
            sys.exit(1)

    do_header()

    # デフォルトのディレクトリにインストールするか確認
    pretty.info(
        f"Craftyのデフォルトインストールディレクトリは {defaults['install_dir']} に設定されています"
    )

    # 自動実行（アンアテンデッド）モード
    if not defaults["unattended"]:
        install_use_default = helper.get_user_yesno(
            f"このディレクトリにCraftyをインストールしますか？ {defaults['install_dir']}", timeout=30, default=True
        )
    else:
        install_use_default = True

    do_header()

    if not install_use_default:
        install_dir = pathlib.Path(
            helper.get_user_open_input("Craftyのインストール先をどこにしますか？", timeout=30, default=defaults['install_dir'])
        ).resolve()
    else:
        install_dir = pathlib.Path(defaults["install_dir"]).resolve()

    pretty.info(f"Craftyを {install_dir} にインストールしています")
    logger.info("Craftyを %s にインストールしています", install_dir)

    # インストールディレクトリが存在するか確認
    if not install_dir.is_dir():
        logger.debug("インストールディレクトリ %s はまだ存在しません", install_dir)
        try:
            install_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
            shutil.chown(install_dir, user="crafty", group="crafty")
        except OSError as e:
            logger.critical(
                "インストールディレクトリ %s を作成できませんでした。エラー: %s", install_dir, e
            )
            pretty.critical(
                f"インストールディレクトリ {install_dir} を作成できません。プログラムを終了します"
            )
            if os.geteuid() != 0:
                logger.critical(
                    "この操作には root/sudo 権限が必要な可能性があります。スクリプトを管理者権限で実行すると解決する場合があります"
                )
                pretty.critical(
                    "この操作には root/sudo 権限が必要です。スクリプトを管理者権限で実行すると解決する場合があります。"
                )
            sys.exit(1)

    logger.debug("インストールディレクトリの所有権が正しいか確認しています")
    install_dir_stat = install_dir.stat()
    logger.debug(
        "インストールディレクトリの所有権: %s:%s モード: %s (期待値: crafty:crafty 0755)",
        install_dir.owner(),
        install_dir.group(),
        oct(install_dir_stat.st_mode),
    )
    if not (
        install_dir.owner() == "crafty"
        and install_dir.group() == "crafty"
        and (install_dir_stat.st_mode & 0o777) == 0o755
    ):
        logger.debug("インストールディレクトリの所有権またはモードが一致しませんでした")
        if helper.get_user_yesno(
            "インストールディレクトリの所有者、グループ、または権限が予想と異なります。修正を試みますか？", timeout=30, default=True
        ):
            shutil.chown(install_dir, user="crafty", group="crafty")
            install_dir.chmod(0o755)

    # Javaのセットアップ
    custom_java_path = do_java_install(install_dir)

    # 新規インストールかどうかを確認
    files = os.listdir(install_dir)

    time.sleep(1)

    do_header()

    logger.info("%s 内の古い Crafty インストールを探しています", install_dir)

    if len(files) > 0:
        logger.warning("古い Crafty インストールが検出されました: %s", install_dir)
        pretty.warning(
            "古いCraftyのインストールが検出されました。インストールディレクトリ内のすべてのファイルを移動してから、再度このスクリプトを実行してください。"
        )

        time.sleep(10)
        sys.exit()

    setup_repo(install_dir)

    do_virt_dir_install(starting_dir, install_dir)

    do_header()

    logger.info("シェルスクリプトを作成しています")
    pretty.info("起動および更新用スクリプトを作成しています")

    make_startup_script(install_dir)
    make_update_script(install_dir)

    if not defaults["unattended"]:
        service_answer = helper.get_user_yesno(
            "Crafty用のサービスファイルを作成しますか？", timeout=30, default=True
        )
        if service_answer:
            make_service_script(install_dir)
            make_service_file(install_dir)
    else:
        make_service_script(install_dir)
        make_service_file(install_dir)

    # 権限の問題を修正
    logger.info("%s の所有権の問題を修正しています", install_dir)
    for installed_file in install_dir.glob("**"):
        logger.debug("%s の所有権を変更しています", installed_file)
        shutil.chown(installed_file, user="crafty", group="crafty")

    time.sleep(1)
    do_header()

    pretty.info("一時ディレクトリをクリーンアップしています")
    helper.ensure_dir_exists(temp_dir)

    if not defaults["debug_mode"]:
        shutil.rmtree(temp_dir)

    pretty.info("おめでとうございます！ Craftyのインストールが完了しました！")
    pretty.info(
        "Craftyを実行するためのユーザー 'crafty' を作成しました（Craftyを root や sudo で実行しないでください）。'sudo su crafty -' で crafty ユーザーに切り替えてください。"
    )
    pretty.info(f"インストール場所: {install_dir}")
    pretty.info(
        f"Craftyを実行するには次のコマンドを使用します: {os.path.join(install_dir, 'run_crafty.sh')}"
    )
    pretty.info(
        f"Craftyを更新するには次のコマンドを使用します: {os.path.join(install_dir, 'update_crafty.sh')}"
    )
    if service_answer:
        pretty.info(
            "サービス設定ファイルが /etc/systemd/system/crafty.service に保存されました"
        )
        pretty.info(
            "次のコマンドでCraftyをサービスとして有効化できます: 'sudo systemctl enable crafty.service' "
        )
        pretty.info(
            "次のコマンドでCraftyサービスを開始できます: 'sudo systemctl start crafty.service' "
        )
