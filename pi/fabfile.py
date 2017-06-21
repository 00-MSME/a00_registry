from crypt import crypt
from fabric.api import local, settings, abort, run, env, sudo, put, get, prefix
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import PI_PASSWORD

env.hosts = ["%s:%s" % ("raspberrypi.local", 22)]
env.user = "pi"
env.password = PI_PASSWORD

BOOTSTRAP_VERSION = "0.0.1"
PYTHON_VERSION = "0.0.1"
TEST_VERSION = "0.0.1"
DESKCONTROL_VERSION = "0.0.1"

JESSIE_VERSION = "2017-04-10-raspbian-jessie-lite"


############################################################################
##              Preparing the base disc image from JESSIE_VERSION
############################################################################

"""
    before you can prepare the card you have to connect to your pi. Login and then:

    "sudo su"
    'wpa_passphrase "Container 20" "eggandchips" >> /etc/wpa_supplicant/wpa_supplicant.conf'
    "wpa_cli reconfigure"

    "raspi-config"

    Interfacing Options > SSH > Yes

    reboot
"""


def prepare_card():
    change_password()
    _change_graphics_memory()
    install_docker()
    _add_bootstrap()
    sudo("reboot")


def change_password():
    env.password = "raspberry"
    crypted_password = crypt(PI_PASSWORD, 'salt')
    sudo('usermod --password %s %s' % (crypted_password, env.user), pty=False)


def _change_graphics_memory():
    sudo('echo "gpu_mem=16" >> /boot/config.txt')


def _add_bootstrap():

    build_bootstrap()
    sudo("mkdir -p /opt/augment00")
    put("start.sh", "/opt/augment00/start.sh", use_sudo=True)
    sudo("chmod 755 /opt/augment00/start.sh")

    put("wifi.py", "/opt/augment00/wifi.py", use_sudo=True)
    sudo("chmod 755 /opt/augment00/wifi.py")

    ## add our own rc.local
    sudo("rm /etc/rc.local")
    put("rc.local", "/etc/rc.local", use_sudo=True)
    sudo("chmod 755 /etc/rc.local")
    sudo("chown root /etc/rc.local")
    sudo("chgrp root /etc/rc.local")


def build_bootstrap():
    tag = BOOTSTRAP_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="paulharter/augment00-bootstrap:%s" docker/augment00-bootstrap' % tag)
    sudo('docker tag paulharter/augment00-bootstrap:%s paulharter/augment00-bootstrap:latest' % tag)


def install_docker():

    # install docker
    run("curl -sSL get.docker.com | sh")

    # sets up service
    run("sudo systemctl enable docker")

    # allows pi use to use docker
    run("sudo usermod -aG docker pi")

    # installs cocker compose
    sudo("easy_install pip")
    sudo("pip install docker-compose")


############################################################################
##              Docker commands for building other images                       ##
############################################################################


def docker_login(password):
    sudo ('docker login -u augment00 -p %s' % password)


def build_python():
    tag = PYTHON_VERSION
    # put("docker", "~")
    # sudo('docker build --no-cache=true -t="paulharter/augment00-python:%s" docker/augment00-python' % tag)
    sudo('docker push augment00/augment00-python:%s' % tag)
    sudo('docker tag augment00/augment00-python:%s augment00/augment00-python:latest' % tag)
    sudo('docker push augment00/augment00-python:latest')


def build_test():
    tag = BOOTSTRAP_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="paulharter/augment00-test:%s" docker/augment00-test' % tag)
    sudo('docker push paulharter/augment00-test:%s' % tag)
    sudo('docker tag paulharter/augment00-test:%s paulharter/augment00-test:latest' % tag)
    sudo('docker push paulharter/augment00-test:latest')


def build_deskcontrol():
    tag = DESKCONTROL_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="augment00/augment00-deskcontrol:%s" docker/augment00-deskcontrol' % tag)
    sudo('docker push augment00/augment00-deskcontrol:%s' % tag)
    sudo('docker tag augment00/augment00-deskcontrol:%s augment00/augment00-deskcontrol:latest' % tag)
    sudo('docker push augment00/augment00-deskcontrol:latest')


















