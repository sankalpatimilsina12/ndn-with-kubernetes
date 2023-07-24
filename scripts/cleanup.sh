#!/bin/bash

# Change to current directory
cd "$(dirname "$0")"

microk8s kubectl delete -f ../k8s/namespace.yaml --ignore-not-found
## Release persistent volume claim
microk8s kubectl patch pv datalake-storage --type json -p '[{"op": "remove", "path": "/spec/claimRef"}]'