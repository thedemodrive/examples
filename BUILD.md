# Welcome to Istio Build Guideline

These guidelines use only for Linux, Mac or Window Sub System (Windows OS is not supported)

Istio components only have few external dependencies you need to set up before being able to build and run the code.

1. Setting up Go
2. Setting up Docker
3. Setting up environment variables
4. Build

## Setting up Go

Many Istio components are written in the Go programming language. To build, you'll need a Go development environment. If you haven't set up a Go development environment, please follow [these instructions](https://golang.org/doc/install) to install the Go tools.

Istio currently builds with Go 1.14

## Setting up Docker

Istio has a docker build system for creating and publishing Docker images. To use docker to build you will need:

- **Docker tools**: To download and install Docker follow [these instructions](https://docs.docker.com/install/).

- **Docker hub ID**: If you do not yet have a docker ID account you can follow [these steps](https://docs.docker.com/docker-id/) to create one. This ID will be used in a later step when setting up the environment variables.

- **Docker credential storage**: Istio has moved to a build system which [builds inside a container](https://docs.google.com/document/d/1vBEt4RyHu2Ywqx6CQk8pHm6wrJCIi4UNLw3xrJdHFtA). Credential transfer into the container is a work in progress. Credential transfer works well on Linux.

## Setting up environment variables

Set up your HUB, TAG, and ISTIO. These environment variables are typically added to your `~/.profile`:

```bash
export USER=thedemodrive

# This defines the docker hub to use when running integration tests and building docker images
# eg: HUB="docker.io/istio", HUB="gcr.io/istio-testing"
export HUB="docker.io/$USER"

# This defines the docker tag to use when running integration tests and building docker images
# eg: TAG=1.5.4, TAG=1.6.0-beta.1, TAG=1.7.0-keyfactor.1
export TAG=1.7.0-keyfactor.1

# Path to Istio source code local
export ISTIO=$HOME/istio/istio.io
```

## Build

Build & push Pilot and Proxy images, run following command:

```bash
make docker.push
```

> Note: Images are pushed to docker hub

Build `istioctl`:

```bash
make istioctl-all
```

> Note: output `istioctl-linux-amd64`, `istioctl-osx`, `istioctl-win.exe`

Build manifests:

```bash
./operator/scripts/create_release_charts.sh -o $PATH_TO_OUTPUT_CHARTS
```

Run local build on kubernetes:

- Update **hub** and **tag** within Istio's config `integrate-keyfactor-ca.yaml`:

```yaml
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: example-integrate-keyfactor-ca
spec:
  profile: demo
  values:
    global:
      hub: thedemodrive
      tag: final-01
...

```

- Use `istioctl` above, and run following command:

```bash
./istioctl manifest --set installPackagePath=$PATH_TO_OUTPUT_CHARTS apply -f ./integrate-keyfactor-ca.yaml
```
