#!/bin/bash

set -eu -o pipefail

wget https://github.com/containerd/nerdctl/releases/download/v0.23.0/nerdctl-full-0.23.0-linux-amd64.tar.gz -O /tmp/nerdctl.tar.gz
echo "2097ffb95c6ce3d847ca4882867297b5ab80e3daea6f967e96ce00cc636981b6  /tmp/nerdctl.tar.gz" | sha256sum -c

tar Cxzvvf /usr/local /tmp/nerdctl.tar.gz

wget https://github.com/google/go-containerregistry/releases/download/v0.11.0/go-containerregistry_Linux_x86_64.tar.gz -O /tmp/go-containerregistry_Linux_x86_64.tar.gz
echo "3cec40eb0fac2e6ed4b71de682ae562d15819ab92145e4f669b57baf04797adb /tmp/go-containerregistry_Linux_x86_64.tar.gz" | sha256sum -c

tar Cxzvvf /usr/local/bin/ /tmp/go-containerregistry_Linux_x86_64.tar.gz

crane -h
