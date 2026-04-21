#!/bin/bash

set -eu -o pipefail

declare -A GOARCH_MAP=([x86_64]="amd64" [aarch64]="arm64")
declare -A CRANE_ARCH_MAP=([x86_64]="x86_64" [aarch64]="arm64")
declare -A CHECKSUMS=(
  [nerdctl-full-2.0.3-linux-amd64.tar.gz]="91bfb8faec1673f3e7c3a020812acffc50a7d7dd82019461f6cfa46435240903"
  [nerdctl-full-2.0.3-linux-arm64.tar.gz]="2a97f78e14cb3e024068d936c8fb801365981e5b48577e278907079de47e4d2c"
  [go-containerregistry_Linux_x86_64.tar.gz]="c14340087103ba9dadf61d45acd20675490fd0ccbd56ac7901fc1b502137f44b"
  [go-containerregistry_Linux_arm64.tar.gz]="aff0db48825124c9331ea310057214bd4e92c01aa2e414d539e9659841d9422a"
)

wget_and_check() {
  local url="$1"
  local dest="$2"
  local file
  file=$(basename "$url")

  wget "$url" -O "$dest"

  local expected="${CHECKSUMS[$file]:-}"
  if [[ -z "$expected" ]]; then
    echo "No checksum found for $file"
    exit 1
  fi
  echo "${expected}  ${dest}" | sha256sum -c
}

MACHINE=$(uname -m)
GOARCH="${GOARCH_MAP[$MACHINE]}"
CRANE_ARCH="${CRANE_ARCH_MAP[$MACHINE]}"

if [[ -z "$GOARCH" ]]; then
  echo "Unsupported architecture: $MACHINE"
  exit 1
fi

NERDCTL_FILE="nerdctl-full-2.0.3-linux-${GOARCH}.tar.gz"
wget_and_check "https://github.com/containerd/nerdctl/releases/download/v2.0.3/${NERDCTL_FILE}" /tmp/nerdctl.tar.gz
tar Cxzvvf /usr/ /tmp/nerdctl.tar.gz

CRANE_FILE="go-containerregistry_Linux_${CRANE_ARCH}.tar.gz"
wget_and_check "https://github.com/google/go-containerregistry/releases/download/v0.20.2/${CRANE_FILE}" /tmp/go-containerregistry.tar.gz
tar Cxzvvf /usr/bin/ /tmp/go-containerregistry.tar.gz

crane -h
