#!/bin/bash

set -eu -o pipefail

wget https://github.com/containerd/nerdctl/releases/download/v1.7.6/nerdctl-full-1.7.6-linux-amd64.tar.gz -O /tmp/nerdctl.tar.gz
echo "2c841e097fcfb5a1760bd354b3778cb695b44cd01f9f271c17507dc4a0b25606  /tmp/nerdctl.tar.gz" | sha256sum -c

tar Cxzvvf /usr/local /tmp/nerdctl.tar.gz

wget https://github.com/google/go-containerregistry/releases/download/v0.20.2/go-containerregistry_Linux_x86_64.tar.gz -O /tmp/go-containerregistry_Linux_x86_64.tar.gz
echo "c14340087103ba9dadf61d45acd20675490fd0ccbd56ac7901fc1b502137f44b /tmp/go-containerregistry_Linux_x86_64.tar.gz" | sha256sum -c

tar Cxzvvf /usr/local/bin/ /tmp/go-containerregistry_Linux_x86_64.tar.gz

crane -h
