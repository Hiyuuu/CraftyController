#!/usr/bin/env python3

import os
import sys
import json
import time
import argparse
import distro as pydistro
import shutil
import platform
import logging
import subprocess

from app.helper import helper
from app.pretty import pretty

with open("config.json", "r") as fh:
    defaults = json.load(fh)

    parser = argparse.ArgumentParser("Crafty Controller - A Server Management System")

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Sets logging level to debug."
    )

    args = parser.parse_args()
    if args.debug:
        defaults["debug_mode"] = args.debug
        pretty.info("Debug mode turned on")


# our pretty header
def do_header():
    time.sleep(2)

    if not defaults["debug_mode"]:
        helper.clear_screen()

    msg = "-" * 25
    msg += "# \t \t Crafty Controller 4.0 Linux Installer \t \t #"
    msg += "-" * 25
    msg += "\n \t\t\t This program will install Crafty Controller 4.0 on your Linux Machine"
    msg += "\n \t\t\t This program isn't perfect, but it will do it's best to get you up an running"

    msg += "\n"
    pretty.header(msg)


# here we can define other distro shell scripts for even better support
def do_distro_install(distro):
    real_dir = os.path.abspath(os.curdir)

    pretty.warning(
        "This install could take a long time depending on how old your system is."
    )
    pretty.warning(
        "Please be patient and do not exit the installer otherwise things may break"
    )
    if distro == "ubuntu_20_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_20_04.sh")

    elif distro == "ubuntu_20_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_20_10.sh")

    elif distro == "ubuntu_21_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_21_04.sh")

    elif distro == "ubuntu_21_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_21_10.sh")

    elif distro == "ubuntu_22_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_22_04.sh")

    elif distro == "ubuntu_22_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "ubuntu_22_10.sh")

    elif distro == "pop_20_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "pop_20_04.sh")

    elif distro == "pop_20_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "pop_20_10.sh")

    elif distro == "pop_21_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "pop_21_04.sh")

    elif distro == "pop_21_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "pop_21_10.sh")

    elif distro == "pop_22_04.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "pop_22_04.sh")

    elif distro == "centos.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "centos.sh")

    elif distro == "debian_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "debian_10.sh")

    elif distro == "debian_11.sh":
        pretty.info("We are updating python3, open-jdk, temurin and pip")
        script = os.path.join(real_dir, "app", "debian_11.sh")

    elif distro == "rocky.sh":
        pretty.info("We are updating python3, open-jdk, temurin and pip")
        script = os.path.join(real_dir, "app", "rocky.sh")

    elif distro == "raspbian_10.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "raspbian_10.sh")

    elif distro == "raspbian_11.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "raspbian_11.sh")

    elif distro == "mint_20.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "mint_20.sh")

    elif distro == "mint_20_2.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "mint_20_2.sh")

    elif distro == "mint_20_3.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "mint_20_3.sh")

    elif distro == "mint_21.sh":
        pretty.info("We are updating python3, open-jdk and pip")
        script = os.path.join(real_dir, "app", "mint_21.sh")

    elif distro == "arch.sh":
        pretty.info("We are updating python, open-jdk, and pip")
        script = os.path.join(real_dir, "app", "arch.sh")
    elif distro == "fedora.sh":
        pretty.info("We are updating python3, open-jdk, pip, and libffi")
        script = os.path.join(real_dir, "app", "fedora.sh")

    else:
        pretty.critical("Unknown Distro: {}".format(distro))
        sys.exit(1)

    logger.info("Running {}".format(script))

    # resp = subprocess.check_output("app/ubuntu_install_depends.sh", shell=True)
    try:
        # Going to ensure our script has full permissions.
        os.chmod(script, 0o0775)
        p = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            sys.stdout.write(line.decode("utf-8"))

    except Exception as e:

        pretty.critical("Error installing dependencies: {}".format(e))
        logger.critical("Error installing dependencies: {}".format(e))


# creates the venv and clones the git repo
def setup_repo():
    do_header()

    # create new virtual environment
    pretty.info("Creating New Virtual Environment")

    venv_dir = os.path.join(install_dir, "venv")

    # changing to install dir
    os.chdir(install_dir)
    pretty.info("Jumping into install directory: {}".format(os.path.abspath(os.curdir)))
    logger.info("Changed directory to: {}".format(os.path.abspath(os.curdir)))

    # creating venv
    try:
        subprocess.check_output(
            "{py} -m venv {dir}".format(py=sys.executable, dir=venv_dir), shell=True
        )
    except Exception as e:
        logger.critical("Unable to create virtual environment!")
        logger.critical("Error: {}".format(e))
        helper.cleanup_bad_install(install_dir)
        sys.exit(1)

    # Ask if they have ssh
    pretty.info("To start, how would you like to authenticate?")
    if not defaults["unattended"]:
        clone_method = helper.get_user_valid_input(
            "Choose SSH if you have a gitlab ssh key set up, otherwise, choose HTTPS.",
            ["ssh", "https"],
        )
    else:
        clone_method = defaults["clone_method"]

    # cloning the repo
    pretty.info("Cloning the Git Repo...this could take a few moments")
    if clone_method == "ssh":
        clone_repo_ssh()
    else:
        clone_repo_https()


def confirm_ssh_key_location(key_location):
    if key_location == None:
        key_location = helper.get_user_open_input(
            "Unable to detect ssh key - Please input the full path to your ssh key"
        )

    if not helper.check_file_exists(key_location):
        pretty.warning("The specified key does not exist!")
        return confirm_ssh_key_location(None)

    key_confirm = helper.get_user_valid_input(
        "SSH key selected from {}. Would you like to use this key?".format(
            key_location
        ),
        ["y", "n"],
    )

    if key_confirm == "y":
        return key_location
    else:
        key_location = helper.get_user_open_input(
            "Please specify the full path of the ssh key you wish to use"
        )
        return confirm_ssh_key_location(key_location)


def clone_repo_ssh():
    invoking_user = os.getenv("SUDO_USER", "root")
    user_ssh_dir = "/home/{}/.ssh/".format(invoking_user)
    if helper.check_file_exists(user_ssh_dir + "id_ed25519"):
        ssh_key_loc = confirm_ssh_key_location(user_ssh_dir + "id_ed25519")
    elif helper.check_file_exists(user_ssh_dir + "id_rsa"):
        ssh_key_loc = confirm_ssh_key_location(user_ssh_dir + "id_rsa")
    else:
        ssh_key_loc = confirm_ssh_key_location(None)
    try:
        subprocess.check_output(
            'git clone git@gitlab.com:crafty-controller/crafty-4.git  --config core.sshCommand="ssh -i {}"'.format(
                ssh_key_loc
            ),
            shell=True,
        )
    except Exception as e:
        logger.critical("Error: {}".format(e))
        logger.critical("Git clone failed! Did you specify the correct key?")
        pretty.critical("Failed to clone. Falling back to HTTPS.")
        clone_repo_https()


def clone_repo_https():
    try:
        subprocess.check_output(
            "git clone https://gitlab.com/crafty-controller/crafty-4.git", shell=True
        )
    except Exception as e:
        logger.critical("Git clone failed!")
        logger.critical("Error: {}".format(e))
        pretty.critical("Unable to clone. Please check the install.log for details!")
        pretty.warning("Cleaning up partial install and exiting...")
        helper.cleanup_bad_install(install_dir)
        sys.exit(1)


# this switches to the branch chosen and does the pip install and such
def do_virt_dir_install():
    do_header()

    # choose your destiny
    pretty.info("Choose your destiny:")
    pretty.info("Crafty comes in different branches:")
    pretty.info("Master - Kinda Stable, a few bugs present")
    pretty.info("Dev - Highly Unstable, full of bugs and new features")

    # unattended
    if not defaults["unattended"]:
        branch = helper.get_user_valid_input(
            "Which branch of Crafty would you like to run?", ["master", "dev"]
        )

    else:
        branch = defaults["branch"]

    # changing to git repo dir
    os.chdir(os.path.join(install_dir, "crafty-4"))
    pretty.info("Jumping into repo directory: {}".format(os.path.abspath(os.curdir)))
    logger.info("Changed directory to: {}".format(os.path.abspath(os.curdir)))

    logger.info("User choose {} branch".format(branch))

    # default empty output
    git_output = ""

    # branch selection
    if branch == "master":
        pretty.info("Slow and Stable it is")

    elif branch == "dev":
        pretty.info("Way to saddle up cowboy!")

    # create a quick script / execute pip install
    do_pip_install(branch)


# installs pip requirements via shell script
def do_pip_install(branch):
    os.chmod(os.path.join(starting_dir, "app", "pip_install_req.sh"), 0o0775)
    src = os.path.join(starting_dir, "app", "pip_install_req.sh")
    dst = os.path.join(install_dir, "pip_install_req.sh")

    logger.info("Copying PIP install script")
    shutil.copyfile(src, dst)

    pip_command = "{} '{}' {}".format(dst, install_dir, branch)

    logger.info("Chmod +x {}".format(dst))
    subprocess.check_call("chmod +x {}".format(dst), shell=True)

    logger.info("Running Pip: {}".format(pip_command))
    pretty.warning(
        "We are now going to install all the python modules for Crafty - This process can take awhile "
        "depending on your internet connection"
    )

    time.sleep(3)

    try:
        p = subprocess.Popen([pip_command], shell=True, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            sys.stdout.write(line.decode("utf-8"))

        # pip_output = subprocess.check_output(pip_command, shell=True)
        # logger.info("Pip output: \n{}".format(pip_output))

    except Exception as e:
        logger.error("Pip failed due to error: {}".format(e))

    if not defaults["debug_mode"]:
        os.remove(dst)


# Creates the run_crafty.sh
def make_startup_script():
    os.chdir(install_dir)
    logger.info("Changing to {}".format(os.path.abspath(os.curdir)))

    txt = "#!/bin/bash\n"
    txt += "cd {}\n".format(install_dir)
    txt += "source venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += "exec python{} main.py \n".format(sys.version_info.major)
    with open("run_crafty.sh", "w") as fh:
        fh.write(txt)
        fh.close()

    subprocess.check_output("chmod +x *.sh", shell=True)


# Creates the update_crafty.sh
def make_update_script():
    os.chdir(install_dir)
    logger.info("Changing to {}".format(os.path.abspath(os.curdir)))

    txt = "#!/bin/bash\n"
    txt += "cd {}\n".format(install_dir)
    txt += "source venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += "git pull \n"
    txt += "pip3 install -r requirements.txt \n"
    with open("update_crafty.sh", "w") as fh:
        fh.write(txt)
        fh.close()

    subprocess.check_output("chmod +x *.sh", shell=True)


# Creates the run as a service.sh
def make_service_script():
    os.chdir(install_dir)
    logger.info("Changing to {}".format(os.path.abspath(os.curdir)))

    txt = "#!/bin/bash\n"
    txt += "cd {}\n".format(install_dir)
    txt += "source venv/bin/activate \n"
    txt += "cd crafty-4 \n"
    txt += "python{} main.py -d\n".format(sys.version_info.major)
    with open("run_crafty_service.sh", "w") as fh:
        fh.write(txt)
        fh.close()

    subprocess.check_output("chmod +x *.sh", shell=True)


def make_service_file():
    os.chdir(install_dir)
    logger.info("Changing to {}".format(os.path.abspath(os.curdir)))
    txt = """
[Unit]
Description=Crafty 4
After=network.target

[Service]
Type=simple

User=crafty
WorkingDirectory={0}

ExecStart=/usr/bin/bash {0}/run_crafty_service.sh

Restart=on-failure
# Other restart options: always, on-abort, etc

# The install section is needed to use
# `systemctl enable` to start on boot
# For a user service that you want to enable
# and start automatically, use `default.target`
# For system level services, use `multi-user.target`
[Install]
WantedBy=multi-user.target
""".format(
        install_dir
    )

    with open("crafty.service", "w") as fh:
        fh.write(txt)
        fh.close()

    subprocess.check_output(
        "cp crafty.service /etc/systemd/system/crafty.service", shell=True
    )


# get distro
def get_distro():
    id = pydistro.id()
    version = pydistro.version()
    sys.stdout.write(
        "We detected your os is: {id} - Version: {version}\n".format(
            id=id, version=version
        )
    )

    file = False

    if id == "debian":
        if version == "10":
            logger.info("Debian 10 'Buster' Detected")
            file = "debian_10.sh"
        if version == "11":
            logger.info("Debian 11 'Bullseye' Detected")
            file = "debian_11.sh"
        else:
            logger.critical("Unsupported Debian - We only support Debian 10 and 11")

    elif id == "raspbian":
        if version == "10":
            logger.info("Raspbian 10 'Buster' Detected")
            file = "raspbian_10.sh"

        if version == "11":
            logger.info("Raspbian 11 'Buster' Detected")
            file = "raspbian_11.sh"
        else:
            logger.critical("Unsupported Raspbian - We only support Raspbian 10 / 11")

    elif id == "pop":
        if version == "20.04":
            logger.info("POP 20.04 Detected")
            file = "pop_20_04.sh"
        elif version == "20.10":
            logger.info("POP 20.10 Detected")
            file = "pop_20_10.sh"
        elif version == "21.04":
            logger.info("POP 21.04 Detected")
            file = "pop_21_04.sh"

        elif version == "21.10":
            logger.info("POP 21.10 Detected")
            file = "pop_21_10.sh"

        elif version == "22.04":
            logger.info("POP 21.04 Detected")
            file = "pop_22_04.sh"

        else:
            logger.critical(
                "Unsupported POP - We only support PopOS 20.04 / 20.10 / 21.04 / 21.10 / 22.04"
            )

    elif id == "ubuntu":
        if version == "20.04":
            logger.info("Ubuntu 20.04 Detected")
            file = "ubuntu_20_04.sh"
        elif version == "20.10":
            logger.info("Ubuntu 20.10 Detected")
            file = "ubuntu_20_10.sh"
        elif version == "21.04":
            logger.info("Ubuntu 21.04 Detected")
            file = "ubuntu_21_04.sh"
        elif version == "21.10":
            logger.info("Ubuntu 21.10 Detected")
            file = "ubuntu_21_10.sh"
        elif version == "22.04":
            logger.info("Ubuntu 22.04 Detected")
            file = "ubuntu_22_04.sh"

        elif version == "22.10":
            logger.info("Ubuntu 22.04 Detected")
            file = "ubuntu_22_10.sh"
        else:
            logger.critical(
                "Unsupported Ubuntu - We only support Ubuntu 20.04 / 20.10 / 21.04 / 21.10 / 22.04 / 22.10"
            )

    elif id == "rocky":
        if version == "8.6":
            logger.info("Rocky 8.6 Detected")
            file = "rocky.sh"
        elif version == "8.7":
            logger.info("Rocky 8.7 Detected")
            file = "rocky.sh"
        elif version == "9.0":
            logger.info("Rocky 9.0 Detected")
            file = "rocky.sh"
        elif version == "9.1":
            logger.info("Rocky 9.1 Detected")
            file = "rocky.sh"
        else:
            logger.critical(
                "Unsupported Distro - We only support Rocky 8.6 / 8.7 / 9.0 / 9.1"
            )

    elif id == "centos":
        if version == "8":
            logger.info("CentOS Stream 8 Detected")
            file = "centos.sh"
        elif version == "9":
            logger.info("CentOS Stream 9 Detected")
            file = "centos.sh"
        else:
            logger.critical("Unsupported Distro - We only support CentOS Stream 8 / 9")

    elif id == "linuxmint":
        if version == "20":
            logger.info("Mint 20 Detected")
            file = "mint_20.sh"
        elif version == "20.2":
            logger.info("Mint 20.2 Detected")
            file = "mint_20_2.sh"
        elif version == "20.3":
            logger.info("Mint 20.3 Detected")
            file = "mint_20_3.sh"
        elif version == "21":
            logger.info("Mint 21 Detected")
            file = "mint_21.sh"
        elif version == "21.1":
            logger.info("Mint 21 Detected")
            file = "mint_21.sh"
        else:
            logger.critical(
                "Unsupported Mint - We only support Mint 20 / 20.2 / 20.3 / 21 / 21.1"
            )

    elif id == "arch" or id == "manjaro" or id == "archarm":
        logger.info("{} version {} Dectected".format(id, version))
        file = "arch.sh"
    elif id == "fedora":
        if version == "35":
            logger.info("Fedora 35 Detected")
            file = "fedora.sh"
        elif version == "36":
            logger.info("Fedora 36 Detected")
            file = "fedora.sh"
        elif version == "37":
            logger.info("Fedora 37 Detected")
            file = "fedora.sh"
        else:
            logger.critical(
                "Unsupported Fedora version - We only support Fedora 35 / 36 / 37"
            )
    if not file:
        logger.critical(
            "Unable to determine distro: ID:{} - Version:{}".format(id, version)
        )

    return file


if __name__ == "__main__":

    logging.basicConfig(
        filename="installer.log",
        filemode="w",
        format="[+] Crafty Installer: %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    logger = logging.getLogger(__name__)

    logger.info("Installer Started")

    starting_dir = os.path.abspath(os.path.curdir)
    temp_dir = os.path.join(starting_dir, "temp")

    do_header()

    # are we on linux?
    if platform.system() != "Linux":
        pretty.critical("This script requires Linux")
        logger.critical("This script requires Linux")
        sys.exit(1)

    pretty.info("Linux Check Success")
    pretty.info(
        "Python Version Check - {}.{}".format(
            sys.version_info.major, sys.version_info.minor
        )
    )

    distro = get_distro()
    if not distro:
        pretty.critical("Your distro is not supported.")
        logger.critical("Unable to find distro information")
        sys.exit(1)

    # default py_check
    py_check = False

    # are we at least on 3.8?
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        pretty.critical("This script requires Python 3.8 or higher!")
        pretty.critical(
            "You are using Python {}.{}.".format(
                sys.version_info.major, sys.version_info.minor
            )
        )
        logger.critical(
            "Python Version < 3.8: {}.{} was found".format(
                sys.version_info.major, sys.version_info.minor
            )
        )
        time.sleep(1)
        pretty.warning(
            "Your python version didn't check out - do you want us to fix this for you?"
        )
    else:
        py_check = True

    # unattended
    if not defaults["unattended"]:
        install_requirements = helper.get_user_valid_input(
            "Install {} requirements?".format(distro), ["y", "n"]
        )
    else:
        install_requirements = "y"

    if install_requirements == "y":
        pretty.info(
            "Installing required packages for {} - Please enter sudo password when prompted".format(
                distro
            )
        )
        do_distro_install(distro)
    else:
        if not py_check:
            pretty.critical("This script requires Python 3.8 or higher!")
            helper.cleanup_bad_install()
            sys.exit(1)

    do_header()

    # do we want to install to default dir?
    pretty.info(
        "Crafty's Default install directory is set to: {}".format(
            defaults["install_dir"]
        )
    )

    # unattended
    if not defaults["unattended"]:
        install_dir = helper.get_user_valid_input(
            "Install Crafty to this directory? {}".format(defaults["install_dir"]),
            ["y", "n"],
        )
    else:
        install_dir = "y"

    do_header()

    if install_dir == "n":
        install_dir = helper.get_user_open_input(
            "Where would you like Crafty to install to?"
        )
    else:
        install_dir = defaults["install_dir"]

    pretty.info("Installing Crafty to {}".format(install_dir))
    logger.info("Installing Crafty to {}".format(install_dir))

    # can we write to the dir?
    if not helper.check_writeable(install_dir):
        pretty.warning("Unable to write to {} - Permission denied".format(install_dir))
        logger.warning("Unable to write to {} - Permission denied".format(install_dir))

        # unattended
        if not defaults["unattended"]:
            own_install_dir = helper.get_user_valid_input(
                "Do you want us to fix this permission issue?", ["y", "n"]
            )
        else:
            own_install_dir = "y"

        if own_install_dir == "y":
            try:
                # make a temp dir
                helper.ensure_dir_exists(temp_dir)

                # let's create a quick sh script to create the dir as root, and then chown the dir to the current user
                fix_perms_sh = os.path.join(temp_dir, "fix_perms.sh")

                with open(fix_perms_sh, "w") as fh:
                    txt = "#!/bin/bash\n"
                    txt += "sudo mkdir -p {}\n".format(install_dir)
                    txt += "sudo chown crafty:crafty {}\n".format(install_dir)
                    fh.write(txt)
                    fh.close()

                    subprocess.check_output(
                        "chmod +x {}".format(fix_perms_sh), shell=True
                    )
                    subprocess.check_output(fix_perms_sh, shell=True)

                    if not helper.check_writeable(install_dir):
                        logger.critical(
                            "Unable to fix permissions issue after shell script"
                        )
                        pretty.critical("Unable to fix permissions issue")
                        sys.exit(1)

            except Exception as e:
                logger.critical("Unable to fix permissions issue")
                pretty.critical("Unable to fix permissions issue")

            # after changing the ownership, let's see if we can write to it now.
            if not helper.check_writeable(install_dir):
                logger.critical(
                    "{} is still unwritable - Unable to fix permissions issue".format(
                        install_dir
                    )
                )
                sys.exit(1)

    # is this a fresh install?
    files = os.listdir(install_dir)

    time.sleep(1)

    do_header()

    logger.info("Looking for old crafty install in: {}".format(install_dir))

    if len(files) > 0:
        logger.warning("Old Crafty install detected: {}".format(install_dir))
        pretty.warning(
            "Old Crafty Install Detected. Please move all files out of the install"
            + " directory and run this script again."
        )

        time.sleep(10)
        sys.exit()

    setup_repo()

    do_virt_dir_install()

    do_header()

    logger.info("Creating Shell Scripts")
    pretty.info("Making start and update scripts for you")

    make_startup_script()
    make_update_script()

    service_answer = helper.get_user_valid_input(
        "Would you like to make a service file for Crafty?", ["y", "n"]
    )
    if service_answer == "y":
        make_service_script()
        make_service_file()

    # fixing permission issues
    cmd = "sudo chown crafty:crafty -R {dir} && sudo chmod 2775 -R {dir}".format(
        dir=install_dir
    )
    subprocess.check_output(cmd, shell=True)

    time.sleep(1)
    do_header()

    pretty.info("Cleaning up temp dir")
    helper.ensure_dir_exists(temp_dir)

    if not defaults["debug_mode"]:
        shutil.rmtree(temp_dir)

    pretty.info("Congrats! Crafty is now installed!")
    pretty.info(
        "We created a user called 'crafty' for you to run crafty as. (DO NOT RUN CRAFTY WITH ROOT OR SUDO) Switch to crafty user with 'sudo su crafty -'"
    )
    pretty.info("Your install is located here: {}".format(install_dir))
    pretty.info(
        "You can run crafty by running {}".format(
            os.path.join(install_dir, "run_crafty.sh")
        )
    )
    pretty.info(
        "You can update crafty by running {}".format(
            os.path.join(install_dir, "update_crafty.sh")
        )
    )
    if service_answer:
        pretty.info(
            "A service unit file has been saved in /etc/systemd/system/crafty.service"
        )
        pretty.info(
            "You will need to run Crafty once normally to get the admin password before enabling the service or running the command 'sudo systemctl status crafty.service' after starting the service"
        )
        pretty.info(
            "run this command to enable crafty as a service- 'sudo systemctl enable crafty.service' "
        )
        pretty.info(
            "run this command to start the crafty service- 'sudo systemctl start crafty.service' "
        )
