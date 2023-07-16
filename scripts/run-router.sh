#!/bin/bash

POD=$(microk8s kubectl get pod -l app=router -n ns-0 -o jsonpath="{.items[0].metadata.name}")
microk8s kubectl exec $POD -n ns-0 -- /bin/sh -c "`cat scripts/router.sh.cp`"