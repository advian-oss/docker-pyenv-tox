#!/usr/bin/env python3
"""Create buildx commands"""
import os
import sys
import datetime

PLATFORMS = ["linux/amd64", "linux/arm64"]
TARGETS = ["pyenv", "tox-base"]
VARIANTS = ["alpine-3.20", "debian-bullseye", "ubuntu-jammy"]
VARIANTS += ["alpine-3.21", "debian-bookworm", "ubuntu-noble"]
# Which distro version gets the distro name tag
DISTRO_DEFAULT_VERSIONS = {
    "alpine": "3.21",
    "debian": "bookworm",
    "ubuntu": "noble",
}
BUILD_PYTHON_VERSIONS = "3.11 3.12 3.13 3.10 3.9"


def print_bakefile(reponame: str, target: str) -> None:
    """Print the bakefile"""
    hcl_targets = ""
    for variant in VARIANTS:
        isodate = datetime.datetime.utcnow().date().isoformat()
        distro, version = variant.split("-")
        distrotag = ""
        if version == DISTRO_DEFAULT_VERSIONS[distro]:
            distrotag = f'"{reponame}/{target}:{distro}", "{reponame}/{target}:{distro}-{isodate}", '
        dockerfile = f"Dockerfile_{distro}"
        hcl_targets += f"""
target "{target}-{variant.replace(".","")}" {{
    dockerfile = "{dockerfile}"
    platforms = [{", ".join(f'"{platform}"' for platform in PLATFORMS)}]
    target = "{target}"
    args = {{
        IMAGE_VERSION = "{version}"
        BUILD_PYTHON_VERSIONS = "{BUILD_PYTHON_VERSIONS}"
    }}
    tags = [{distrotag}"{reponame}/{target}:{distro}-{version}", "{reponame}/{target}:{distro}-{version}-{isodate}"]
}}
"""

    print(
        f"""
// To build and push images, redirect this output to a file named "{target}.hcl" and run:
//
// docker login
// docker buildx bake --push --file ./{target}.hcl

group "default" {{
    targets = [{", ".join(f'"{target}-{variant.replace(".","")}"' for variant in VARIANTS)}]
}}"""
    )
    print(hcl_targets)


if __name__ == "__main__":
    envreponame = os.environ.get("DHUBREPO")
    if not envreponame:
        print("Define DHUBREPO")
        sys.exit(1)

    if len(sys.argv) != 2 or not sys.argv[1] in TARGETS:
        print(f"""Specify target, one of: {", ".join(TARGETS)}""")
        sys.exit(1)
    clitarget = sys.argv[1]
    print_bakefile(envreponame, clitarget)
