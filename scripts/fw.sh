#!/bin/bash

echo "Activating forwarder...."
jq -n '{
  mempool: {
    DIRECT: { capacity: 1048575, dataroom: 9146 },
    INDIRECT: { capacity: 1048575 }
  },
  pcct: {
    pcctCapacity: 65535,
    csMemoryCapacity: 20000,
    csIndirectCapacity: 20000
  }
}' | ndndpdk-ctrl activate-forwarder

echo "Creating faces to router...."
RETRIEVE_ROUTERFACEID=$(jq -n '{
    scheme: "udp",
    local: "retrieve-service.physics-namespace.svc.cluster.local:6363",
    remote: "service-0.ns-0.svc.cluster.local:6363",
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)

SUBSET_ROUTERFACEID=$(jq -n '{
    scheme: "udp",
    local: "subset-service.physics-namespace.svc.cluster.local:6363",
    remote: "service-0.ns-0.svc.cluster.local:6363",
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)

echo "Creating face to fileserver"
FSFACEID=$(jq -n '{
  scheme: "memif",
  socketName: "/run/ndn/fileserver.sock",
  id: 0,
  role: "server",
  dataroom: 9000
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)

echo "Inserting FIB entry for /k8s/retrieve-service/physics to fileserver"
ndndpdk-ctrl insert-fib --name /k8s/retrieve-service/physics --nexthop $FSFACEID

echo "Inserting FIB entry for /k8s/subset-service/physics to fileserver"
ndndpdk-ctrl insert-fib --name /k8s/subset-service/physics --nexthop $FSFACEID

echo "Done."
