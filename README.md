# docker-pyenv-tox

Dockerfiles and helper scripts for multi-arch pyenv and tox on top of the pyenv images

Alpine and Debian Buster(-slim) based variants (just in case you have something that chokes
on musl-libc on alpine)

### Building images

There's a helper script to generate the pile of commands needed for all tag versions

    DHUBREPO=myrepo IMGARCH=`uname -m` ./create_builds.py

This will give you the commands to build and tag images (also for pushing them to docker hub)

Then for multi-arh manifests are needed, time to call another helper

    DHUBREPO=myrepo ./create_manifests.py
