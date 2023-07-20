: '
This script is responsible for performing the following tasks:
1. setting up a microk8s Kubernetes cluster and NFS server
2. run NFD on gateway app
3. run NFD & ndn6-file-server on the datalake app
4. The gateway app's NFD should have /ndn/k8s/data pointing to the datalake app's NFD
5. Load NCBI data into the datalake
'

#!/bin/bash

# Ensure prerequisites are setup
source ./prerequisites.sh

# Create deployments
microk8s kubectl apply -f namespace.yaml,pvc.yaml,dataloader.yaml,gateway.yaml,datalake.yaml

# Check if pods are ready
deployments=("gw" "dl")
for deployment in "${deployments[@]}"; do
    while [[ $(microk8s kubectl get pods -n ndnk8s -l app=$deployment -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do
        echo "Waiting for pods in $deployment deployment to be ready..."
        sleep 5
    done
    echo "All pods in $deployment deployment are ready..."
done

# Register prefixes on gateway deployment
POD_NAME=$(microk8s kubectl get pods -n ndnk8s -l app=gw --no-headers -o custom-columns=":metadata.name")
microk8s kubectl exec -n ndnk8s $POD_NAME -- nfdc face create remote udp4://dl-nfd.ndnk8s.svc.cluster.local:6363
microk8s kubectl exec -n ndnk8s $POD_NAME -- nfdc route add prefix /ndn/k8s/data nexthop udp4://dl-nfd.ndnk8s.svc.cluster.local:6363

# Wait for dataloader job to finish
echo -n "Waiting for dataloader job to complete..."
while [[ $(microk8s kubectl get jobs -n ndnk8s ndnk8s-dataloader -o 'jsonpath={..status.conditions[?(@.type=="Complete")].status}') != "True" ]]; do
    echo "."
    sleep 5
done

echo ""
echo "Setup complete..."
