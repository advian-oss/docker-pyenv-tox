#!/usr/bin/env python3
"""Create manifest commands"""
import os
import sys
import subprocess
import itertools

from create_manifests import VARIANTS, ARCHS, TARGETS

if __name__ == "__main__":
    reponame = os.environ.get("DHUBREPO")
    if not reponame:
        print("Define DHUBREPO")
        sys.exit(1)
    archname = os.environ.get("IMGARCH")
    if not archname:
        print("Define IMGARCH")
        if archname not in ARCHS:
            print("IMGARCH must be one of {}".format(ARCHS))
        sys.exit(1)
    build_commands = []
    push_commands = [["docker", "login"]]
    for variant in VARIANTS:
        distro, version = variant.split("-")
        dockerfile = f"Dockerfile_{distro}"
        for target in TARGETS:
            buildcmd = ["docker", "build", "--build-arg", f"IMAGE_VERSION={version}", "--target", target]
            for tag in ["", version]:
                tagstr = f"{target}:{archname}-{distro}"
                if tag:
                    tagstr += f"-{tag}"
                repotag = reponame + "/" + tagstr
                buildcmd += ["-t", tagstr, "-t", repotag]
                push_commands.append(["docker", "push", repotag])
            buildcmd += ["-f", dockerfile, "."]
            build_commands.append(buildcmd)

    if os.environ.get("AUTORUN"):
        for cmd in itertools.chain(build_commands, push_commands):
            subprocess.run(" ".join(cmd), check=True, shell=True)
    else:
        print("** Run the following commands:")
        for cmd in itertools.chain(build_commands, push_commands):
            print(" ".join(cmd))
