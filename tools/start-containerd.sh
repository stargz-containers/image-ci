#!/bin/bash

set -eux -o pipefail

containerd -v
containerd &

sleep 5

# we verify that it works
nerdctl version
nerdctl run --rm ghcr.io/stargz-containers/ubuntu:22.04 echo hello
