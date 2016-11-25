import subprocess


def restart_avx_controller():
    # NB This assumes a suitable entry in /etc/sudoers.d/ to allow the command to run passwordlessly
    return subprocess.call(["/usr/bin/sudo", "/bin/systemctl", "restart", "avx-controller.service"])


def restart_server():
    return subprocess.call(["/bin/systemctl", "reboot"])
