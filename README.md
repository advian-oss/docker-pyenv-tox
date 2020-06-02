# docker-pyenv-tox

Dockerfiles and helper scripts for multi-arch pyenv and tox on top of the pyenv images

Alpine and Debian Buster(-slim) based variants (just in case you have something that chokes
on musl-libc on alpine). For weird corner cases there's also Ubuntu based image (in case there
are some 3rd party binary only deps that don't work on the available debians)

Pre-built images for x64 and arm64 at <https://hub.docker.com/r/advian/pyenv>

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

### Enable `buildx`

On x86 Linux, the following _may_ be necessary to install `buildx`:

    export DOCKER_BUILDKIT=1
    docker build --platform=local -o . git://github.com/docker/buildx
    mkdir -p ~/.docker/cli-plugins
    mv buildx ~/.docker/cli-plugins/docker-buildx

### Enable `docker/binfmt`

In order to be able to build images for foreign architectures, the `docker/binfmt`
image should pulled and run. This will make [`qemu-user-static`](https://github.com/multiarch/qemu-user-static)
available on the host:

    docker run --rm --privileged docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64  # latest as of 2020-06-03

### Create a "builder" instance

    docker buildx create --name toxbuilder
    docker buildx use toxbuilder
    docker buildx inspect --bootstrap

### Build and push

    export DHUBREPO=myrepo
    ./create_builds.py pyenv > pyenv.hcl
    ./create_builds.py tox-base > tox-base.hcl
    docker login
    docker buildx bake --push --file ./pyenv.hcl
    docker buildx bake --push --file ./tox-base.hcl

The `create_builds.py` script output includes the Docker commands above as HCL file comments.
