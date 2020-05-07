# docker-pyenv-tox

Dockerfiles and helper scripts for multi-arch pyenv and tox on top of the pyenv images

Alpine and Debian Buster(-slim) based variants (just in case you have something that chokes
on musl-libc on alpine). For weird corner cases there's also Ubuntu based image (in case there
are some 3rd party binary only deps that don't work on the available debians)

## Using the tox-base image

In your project Dockerfile just add a new target

    FROM advian/tox-base:alpine as tox

That alone is enough unless you have special needs, then you can build and
run the image:

    docker build -t myproject:tox --target tox .
    docker run --rm -it -v `pwd`:/app myproject:tox

If Alpine/musl-libc is a problem you can use `:debian` instead, if you really
need some packages only available for Ubuntu there's `:ubuntu` too.

### Testing

This repo also has a minimal Python package and tox config for quick-testing

    docker build -t toxtest --target tox -f Dockerfile_toxexample .
    docker run --rm -it -v `pwd`:/app toxtest

## Building images

There's a helper script to generate the pile of commands needed for all tag versions

    DHUBREPO=myrepo IMGARCH=`uname -m` ./create_builds.py

This will give you the commands to build and tag images (also for pushing them to docker hub)

Then for multi-arh manifests are needed, time to call another helper

    DHUBREPO=myrepo ./create_manifests.py
