#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Configurations and functions to operate tmate-ssh-server."""

import dataclasses
import ipaddress
import subprocess
import textwrap
import typing
from pathlib import Path

import jinja2
from charms.operator_libs_linux.v0 import apt

APT_DEPENDENCIES = [
    "git-core",
    "build-essential",
    "pkg-config",
    "libtool",
    "libevent-dev",
    "libncurses-dev",
    "zlib1g-dev",
    "automake",
    "libssh-dev",
    "cmake",
    "ruby",
    "libmsgpack-dev",
]

GIT_REPOSITORY_URL = "https://github.com/tmate-io/tmate-ssh-server.git"

WORK_DIR = Path("/home/ubuntu/")
CREATE_KEYS_SCRIPT_PATH = WORK_DIR / "create_keys.sh"
KEYS_DIR = WORK_DIR / "keys"
RSA_PUB_KEY_PATH = KEYS_DIR / "ssh_host_rsa_key.pub"
ED25519_PUB_KEY_PATH = KEYS_DIR / "ssh_host_ed25519_key.pub"
TMATE_SSH_SERVER_SERVICE_PATH = Path("/etc/systemd/system/tmate-ssh-server.service")

PORT = 10022


class DependencyInstallError(Exception):
    """Represents an error while installing dependencies."""


class KeyInstallError(Exception):
    """Represents an error while installing/generating key files."""


class DaemonStartError(Exception):
    """Represents an error while starting tmate-ssh-server daemon."""


class IncompleteInitError(Exception):
    """The tmate-ssh-server has not been fully initialized."""


class FingerPrintError(Exception):
    """Represents an error with generating fingerprints from public keys."""


def install_dependencies():
    """Install dependenciese required to start tmate-ssh-server container."""
    try:
        apt.update()
        apt.add_package(["docker.io", "openssh-client"])
    except (apt.PackageNotFoundError, apt.PackageError) as exc:
        raise DependencyInstallError from exc


def install_keys(host_ip: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str]):
    """Install key creation script and generate keys.

    Args:
        host_ip: The charm host's public IP address.
    """
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"), autoescape=True)
    template = environment.get_template("create_keys.sh.j2")
    script = template.render(keys_dir=KEYS_DIR, host=str(host_ip), port=PORT)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    CREATE_KEYS_SCRIPT_PATH.write_text(script, encoding="utf-8")
    try:
        subprocess.run(["/usr/bin/chown", "-R", "ubuntu:ubuntu", str(WORK_DIR)])
        CREATE_KEYS_SCRIPT_PATH.chmod(755)
        subprocess.check_call(["/usr/bin/sudo", str(CREATE_KEYS_SCRIPT_PATH)])
    except subprocess.CalledProcessError as exc:
        raise KeyInstallError from exc


def start_daemon():
    """Install unit files and start daemon."""
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"), autoescape=True)
    service_content = environment.get_template("tmate-ssh-server.service.j2").render(
        WORKDIR=WORK_DIR,
        KEYS_DIR=KEYS_DIR,
        PORT=PORT,
    )
    TMATE_SSH_SERVER_SERVICE_PATH.write_text(service_content, encoding="utf-8")
    try:
        subprocess.check_call(["/usr/bin/systemctl", "daemon-reload"])
        subprocess.check_call(["/usr/bin/systemctl", "restart", "tmate-ssh-server"])
        subprocess.check_call(["/usr/bin/systemctl", "enable", "tmate-ssh-server"])
    except subprocess.CalledProcessError as exc:
        raise DaemonStartError from exc


@dataclasses.dataclass
class FingerPrints:
    """The public key fingerprints.

    Attributes:
        rsa: The RSA public key fingerprint.
        ed25519: The ed25519 public key fingerprint.
    """

    rsa: str
    ed25519: str


def get_fingerprints() -> FingerPrints:
    """Get fingerprint from generated keys.

    Raises:
        IncompleteInitError: if the keys have not been generated by the create_keys.sh script.
        KeyInstallError: if there was something wrong generating fingerprints from public keys.

    Returns:
        The generated public key fingerprints.
    """
    if not KEYS_DIR.exists() or not RSA_PUB_KEY_PATH.exists() or not ED25519_PUB_KEY_PATH.exists():
        raise IncompleteInitError("Missing keys directory.")
    try:
        rsa_stdout = str(
            subprocess.check_output(
                ["ssh-keygen", "-l", "-E", "SHA256", "-f", str(RSA_PUB_KEY_PATH)]
            ),
            encoding="utf-8",
        ).split()[1]
        ed25519_stdout = str(
            subprocess.check_output(
                ["ssh-keygen", "-l", "-E", "SHA256", "-f", str(ED25519_PUB_KEY_PATH)]
            ),
            encoding="utf-8",
        ).split()[1]
    except subprocess.CalledProcessError as exc:
        raise KeyInstallError("Unable to get pub key fingerprints.") from exc

    return FingerPrints(rsa=rsa_stdout, ed25519=ed25519_stdout)


def generate_tmate_conf(host: str) -> str:
    """Generate the .tmate.conf values from generated keys.

    Args:
        ip_addr: The host IP address.

    Raises:
        FingerPrintError: if there was an error generating fingerprints from public keys.
    """
    try:
        fingerprints = get_fingerprints()
    except (IncompleteInitError, KeyInstallError) as exc:
        raise FingerPrintError("Error generating fingerprints.") from exc

    return textwrap.dedent(
        f"""
        set -g tmate-server-host {host}
        set -g tmate-server-port {PORT}
        set -g tmate-server-rsa-fingerprint {fingerprints.rsa}
        set -g tmate-server-ed25519-fingerprint {fingerprints.ed25519}
        """
    )
