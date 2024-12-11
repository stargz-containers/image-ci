#!/bin/bash

set -eu -o pipefail

wget https://github.com/containerd/nerdctl/releases/download/v2.0.3/nerdctl-full-2.0.3-linux-amd64.tar.gz -O /tmp/nerdctl.tar.gz
echo "91bfb8faec1673f3e7c3a020812acffc50a7d7dd82019461f6cfa46435240903  /tmp/nerdctl.tar.gz" | sha256sum -c

tar Cxzvvf /usr/ /tmp/nerdctl.tar.gz

wget https://github.com/google/go-containerregistry/releases/download/v0.20.2/go-containerregistry_Linux_x86_64.tar.gz -O /tmp/go-containerregistry_Linux_x86_64.tar.gz
echo "c14340087103ba9dadf61d45acd20675490fd0ccbd56ac7901fc1b502137f44b /tmp/go-containerregistry_Linux_x86_64.tar.gz" | sha256sum -c

tar Cxzvvf /usr/bin/ /tmp/go-containerregistry_Linux_x86_64.tar.gz

crane -h
