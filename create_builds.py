#!/usr/bin/env python3
"""Create buildx commands"""
import os
import sys
import datetime

PLATFORMS = ["linux/amd64", "linux/arm64"]
TARGETS = ["pyenv", "tox-base"]
VARIANTS = ["alpine-3.16", "debian-buster", "ubuntu-focal"]
VARIANTS += ["alpine-3.17", "debian-bullseye", "ubuntu-jammy"]
# Which distro version gets the distro name tag
DISTRO_DEFAULT_VERSIONS = {
    "alpine": "3.17",
    "debian": "bullseye",
    "ubuntu": "jammy",
}


if __name__ == "__main__":
    reponame = os.environ.get("DHUBREPO")
    if not reponame:
        print("Define DHUBREPO")
        sys.exit(1)

    if len(sys.argv) != 2 or not sys.argv[1] in TARGETS:
        print(f"""Specify target, one of: {", ".join(TARGETS)}""")
        sys.exit(1)
    target = sys.argv[1]

    hcl_targets = ""
    for variant in VARIANTS:
        isodate = datetime.datetime.utcnow().date().isoformat()
        distro, version = variant.split("-")
        distrotag = ""
        if version == DISTRO_DEFAULT_VERSIONS[distro]:
            distrotag = f'"{reponame}/{target}:{distro}", '
        dockerfile = f"Dockerfile_{distro}"
        hcl_targets += f"""
target "{target}-{variant.replace(".","")}" {{
    dockerfile = "{dockerfile}"
    platforms = [{", ".join(f'"{platform}"' for platform in PLATFORMS)}]
    target = "{target}"
    args = {{
        IMAGE_VERSION = "{version}"
    }}
    tags = [{distrotag}"{reponame}/{target}:{distro}-{isodate}", "{reponame}/{target}:{distro}-{version}", "{reponame}/{target}:{distro}-{version}-{isodate}"]
}}
"""

    print(f"""
// To build and push images, redirect this output to a file named "{target}.hcl" and run:
//
// docker login
// docker buildx bake --push --file ./{target}.hcl

group "default" {{
    targets = [{", ".join(f'"{target}-{variant.replace(".","")}"' for variant in VARIANTS)}]
}}""")
    print(hcl_targets)
