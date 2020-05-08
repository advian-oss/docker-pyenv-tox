#!/usr/bin/env python3
"""Create manifest commands"""
import os
import sys
import subprocess
import itertools


ARCHS = ["x86_64", "aarch64"]
VARIANTS = ["alpine-3.11", "debian-buster", "ubuntu-focal"]
TARGETS = ["pyenv", "tox-base"]


if __name__ == "__main__":
    reponame = os.environ.get("DHUBREPO")
    if not reponame:
        print("Define DHUBREPO")
        sys.exit(1)
    tag_commands = []
    inspect_commands = []
    push_commands = [["docker", "login"]]
    for variant in VARIANTS:
        distro, version = variant.split("-")
        dockerfile = f"Dockerfile_{distro}"
        for target in TARGETS:
            for tag in ["", version]:
                manifestag = f"{reponame}/{target}:{distro}"
                if tag:
                    manifestag += f"-{tag}"
                cmd = ["docker", "manifest", "create", "--amend", manifestag]
                for arch in ARCHS:
                    archtag = f"{reponame}/{target}:{arch}-{distro}"
                    if tag:
                        archtag += f"-{tag}"
                    cmd.append(archtag)
                tag_commands.append(cmd)
                inspect_commands.append("docker manifest inspect {}".format(manifestag))
                push_commands.append(["docker", "manifest", "push", manifestag])

    if os.environ.get("AUTORUN"):
        for cmd in itertools.chain(tag_commands, push_commands):
            subprocess.run(" ".join(cmd), check=True, shell=True)
    else:
        print("** Run the following commands:")
        for cmd in tag_commands:
            print(" ".join(cmd))

    print("** To check results run:")
    for cmd in inspect_commands:
        print(cmd)

    if not os.environ.get("AUTORUN"):
        print("** to push the manifests run:")
        for cmd in push_commands:
            print(" ".join(cmd))
