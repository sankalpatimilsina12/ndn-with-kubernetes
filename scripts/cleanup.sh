#!/bin/bash

microk8s kubectl delete -f namespace.yaml --ignore-not-found
## Release persistent volume claim
microk8s kubectl patch pv datalake-storage --type json -p '[{"op": "remove", "path": "/spec/claimRef"}]'