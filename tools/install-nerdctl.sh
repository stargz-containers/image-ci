set -eu

wget https://github.com/containerd/nerdctl/releases/download/v0.23.0/nerdctl-full-0.23.0-linux-amd64.tar.gz -O /tmp/nerdctl.tar.gz
echo "2097ffb95c6ce3d847ca4882867297b5ab80e3daea6f967e96ce00cc636981b6  /tmp/nerdctl.tar.gz" | sha256sum -c

tar Cxzvvf /usr/local /tmp/nerdctl.tar.gz
