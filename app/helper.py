import logging
import os
import pathlib
import shutil
import subprocess
import time

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

    def get_user_valid_input(self, q, valid_answers):
        while True:
            n = input(
                "\n{}{} - {}{}: ".format(bcolors.BOLD, q, valid_answers, bcolors.ENDC)
            ).lower()
            if n in valid_answers:
                return n

    def get_user_open_input(self, q):
        n = input("\n{}{}{}: ".format(bcolors.BOLD, q, bcolors.ENDC))
        return n

    def ensure_dir_exists(self, path):
        pathlib.Path(path).mkdir(exist_ok=True)

    def check_writeable(self, check_path):
        filepath = pathlib.Path(check_path, "tempfile.txt")
        try:
            filepath.touch()
            filepath.unlink()

            logging.info("{} is writable".format(filename))
            return True

        except Exception as e:
            logging.critical("Unable to write to {} - Error: {}".format(path, e))
            return False

    def check_file_exists(self, path):
        if os.path.exists(path) and os.path.isfile(path):
            logging.debug("Found path: {}".format(path))
            return True
        else:
            return False

    def cleanup_bad_install(self, install_dir):
        shutil.rmtree(install_dir)
        if self.check_file_exists("/etc/systemd/system/crafty.service"):
            os.remove("/etc/systemd/system/crafty.service")


helper = helper_obj()
