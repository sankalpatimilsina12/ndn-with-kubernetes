# This script is responsible for performing the following tasks:
# 1. setup microk8s on the host machine with NFD and ndn6-file-server
# 2. join the host machine to the first machine's cluster
# 3. run the ndn6-file-server

#!/bin/bash

# Setup microk8s
if ! command -v microk8s &>/dev/null; then
    echo "Setting up microk8s..."
    sudo snap install microk8s --classic --channel=1.27
    sudo usermod -a -G microk8s $USER
    sudo chown -f -R $USER ~/.kube
    newgrp microk8s
else
    echo "Microk8s already installed, skipping..."
fi

# Create gateway deployment
microk8s kubectl apply -f datalake.yaml
# Check if gateway pods are running
while [[ $(microk8s kubectl get pods -n dl -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do
    echo "Waiting for datalake pods to be running..."
    sleep 5
done

# Get pod name
POD_NAME=$(microk8s kubectl get pods -n dl --no-headers -o custom-columns=":metadata.name")
echo $POD_NAME
echo "Microk8s setup on the gateway node complete..."