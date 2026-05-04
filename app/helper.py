import logging
import os
import pathlib
import select
import shutil
import subprocess
import sys
import time
from typing import Union

logger = logging.getLogger(__name__)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class helper_obj:

    def clear_screen(self):
        time.sleep(0.5)
        os.system("clear")

    def run_command(self, command_line: list) -> tuple:
        process = subprocess.Popen(
            command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        return out, err

    def _get_input_timeout(self, prompt: str, timeout: int, default: str) -> str:
        sys.stdout.write(f"{prompt} (30秒で自動的に '{default}' が選択されます): ")
        sys.stdout.flush()
        
        # Windows では select.select はソケットに対してのみ動作するため、
        # Linux 環境であることを前提とした実装です（install_crafty.py でチェック済み）。
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().rstrip('\n')
        else:
            print(f"\nタイムアウトしました。デフォルト値 '{default}' を使用します。")
            return default

    def get_user_valid_input(self, q: str, valid_answers: list[str], timeout: int = None, default: str = None) -> str:
        while True:
            prompt = f"\n{bcolors.BOLD}{q} - {valid_answers}{bcolors.ENDC}"
            if timeout is not None and default is not None:
                n = self._get_input_timeout(prompt, timeout, default).lower()
            else:
                n = input(f"{prompt}: ").lower()
                
            if n in valid_answers:
                return n
            
            if timeout is not None:
                # タイムアウトが有効な場合、無効な入力でもデフォルト値を返すようにするか、
                # またはループを抜ける必要があります。ここではデフォルト値を優先します。
                print(f"無効な入力です。デフォルトの '{default}' を使用します。")
                return default

    def get_user_yesno(self, q: str, timeout: int = None, default: bool = True) -> Union[bool|None]:
        default_str = "y" if default else "n"
        response = self.get_user_valid_input(q, ["y", "n"], timeout, default_str)
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            return None

    def get_user_open_input(self, q: str, timeout: int = None, default: str = None) -> str:
        prompt = f"\n{bcolors.BOLD}{q}{bcolors.ENDC}"
        if timeout is not None and default is not None:
            return self._get_input_timeout(prompt, timeout, default)
        
        n = input(f"{prompt}: ")
        return n

    def ensure_dir_exists(self, path):
        pathlib.Path(path).mkdir(exist_ok=True)

    def check_writeable(self, check_path):
        filepath = pathlib.Path(check_path, "tempfile.txt")
        try:
            filepath.touch()
            filepath.unlink()

            logging.info("%s は書き込み可能です", filepath)
            return True

        except Exception as e:
            logging.exception("%s に書き込むことができません - エラー:", check_path, exc_info=e)
            return False

    def check_file_exists(self, check_path):
        if os.path.exists(check_path) and os.path.isfile(check_path):
            logging.debug("パスが見つかりました: %s", check_path)
            return True
        else:
            return False

    def cleanup_bad_install(self, install_dir):
        shutil.rmtree(install_dir)
        if self.check_file_exists("/etc/systemd/system/crafty.service"):
            os.remove("/etc/systemd/system/crafty.service")

    def chmod_add_exec(self, target_file: pathlib.Path):
        fstat = target_file.stat(follow_symlinks=True)
        read_bits = fstat.st_mode & 0o444
        exec_bits = read_bits >> 2
        target_file.chmod(fstat.st_mode | exec_bits)


helper = helper_obj()
