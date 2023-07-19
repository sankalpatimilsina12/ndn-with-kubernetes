: '
This script is responsible for setting up a microk8s Kubernetes cluster and NFS server.
'

#!/bin/bash

# Setup microk8s
if ! command -v microk8s &>/dev/null; then
    echo "Setting up microk8s..."
    sudo snap install microk8s --classic --channel=1.27
else
    echo "Microk8s already installed. Skipping installation..."
fi
# ensure microk8s user and group setup is in place
id -nG "$USER" | grep -qw "microk8s" || {
    sudo usermod -a -G microk8s $USER
    sudo chown -f -R $USER ~/.kube
    newgrp microk8s
}

# Setup NFS server
if ! command -v nfsstat &>/dev/null; then
    echo "Setting up NFS server..."
    sudo apt-get install nfs-kernel-server
else
    echo "NFS server already installed. Skipping installation..."
fi
# ensure NFS server setup is in place
sudo mkdir -p /workspace
sudo chown $USER:$(id -gn) /workspace
grep -qxF '/workspace *(rw,sync,no_subtree_check,no_root_squash)' /etc/exports || sudo bash -c 'echo "/workspace *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports'
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
