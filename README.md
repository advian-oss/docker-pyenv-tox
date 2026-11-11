# docker-pyenv-tox

Dockerfiles and helper scripts for multi-arch pyenv and tox on top of the pyenv images

Alpine and Debian based variants (just in case you have something that chokes
on musl-libc on alpine). For weird corner cases there's also Ubuntu based image (in case there
are some 3rd party binary only deps that don't work on the available debians)

Pre-built images for x64 and arm64 at <https://hub.docker.com/r/advian/pyenv> and
<https://hub.docker.com/r/advian/tox-base> which has tox preinstalled and is generally
the recommended starting point.

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

    docker build --progress=plain -t toxtest --target tox -f Dockerfile_toxexample .
    docker run --rm -it -v `pwd`:/app toxtest

## Building images

### Enable `buildx`

It should be available as part of standard Docker packages these days.

### Create a local builder

Registry cache export requires a `docker-container` Buildx driver. Create a builder once:

```sh
docker buildx create --name toxbuilder --driver docker-container --config "$(pwd)/buildkitd.toml"
docker buildx use toxbuilder
docker buildx inspect --bootstrap
```

### Generate a Bake file

The generated Bake file includes all distro variants and imports the public registry cache by default.
`DHUBREPO` selects the image namespace; the cache repository defaults to `${DHUBREPO}/buildcache`.

```sh
export DHUBREPO=advian
./create_builds.py all > docker-bake.hcl
docker login
```

`all` builds both `pyenv` and `tox-base` targets in one Bake invocation, allowing BuildKit to share
their common stages. `./create_builds.py pyenv` and `./create_builds.py tox-base` remain available
when only one image family is needed.

### Build locally using the shared cache

Choose the architecture of the local machine so the image can be loaded directly without emulation.
For example, on Apple Silicon:

```sh
BUILD_ARCH=arm64 docker buildx bake tox-base-debian-trixie --load --file ./docker-bake.hcl
```

Use `BUILD_ARCH=amd64` on an amd64 machine. Replace the target with e.g. `pyenv-debian-trixie` or
another generated target as needed. Bake imports the matching and opposite-architecture cache refs;
BuildKit reuses the compatible layers, while the local builder also retains its own cache between runs.

To build and push the full multi-platform image set from a machine that supports both architectures:

```sh
docker buildx bake --pull --push --provenance=true --sbom=true --file ./docker-bake.hcl
```

### Cache refresh and publishing

The CI workflow builds natively on amd64 and arm64 runners and exports `mode=max` cache from each
`tox-base` target to `${DHUBREPO}/buildcache:<variant>-<architecture>`. Those public cache refs are
shared with local builds. Publishing cache requires Docker Hub write access; local builds only need
read access. To seed or update a cache from a local machine, run the target for that machine's native
architecture with `CACHE_PUSH=true` (this builds the image layers and exports cache, without publishing
the tagged image):

```sh
BUILD_ARCH=arm64 CACHE_PUSH=true docker buildx bake tox-base-debian-trixie --file ./docker-bake.hcl
```

`CACHE_EPOCH` defaults to the ISO week of `BUILD_DATE`, so the expensive package and Python build
stages are reused within a week and refreshed in the next one. CI passes a single `BUILD_DATE` to its
build and merge jobs to keep dated tags consistent. Override `BUILD_DATE` when generating a Bake file
for a specific release date, or set `CACHE_EPOCH` explicitly to force a cache refresh or match CI
across a week boundary. Changing the epoch invalidates the cached `pyenv_clean` build steps.
