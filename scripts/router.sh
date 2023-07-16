#!/bin/bash

echo "Setting up tunnels...."
ip link add tunnel-client type gretap local 10.142.0.57 remote 10.142.15.197 dev ens4
ip addr add 88.63.36.11/24 dev tunnel-client
ip link set dev tunnel-client address 5c:75:25:5b:d4:1f
ip link set tunnel-client up

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

echo "Creating ethernet ports (af_packet)...."
ndndpdk-ctrl create-eth-port --netif tunnel-client --mtu 1200

echo "Creating face to client...."
CLIENTFACEID=$(jq -n '{
    scheme: "udpe",
    localIP: "88.63.36.11",
    remoteIP: "88.63.36.12",
    localUDP: 6363,
    remoteUDP: 6363,
    local: "5c:75:25:5b:d4:1f",
    remote: "5c:75:25:5b:d4:1e",
    mtu: 1100
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)

echo "Creating faces to next ndn-dpdk forwarder in the data lake...."
NODE1FACEID_RETRIEVE=$(jq -n '{
    scheme: "udp",
    local: "service-0.ns-0.svc.cluster.local:6363",
    remote: "retrieve-service.physics-namespace.svc.cluster.local:6363",
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)
NODE1FACEID_SUBSET=$(jq -n '{
    scheme: "udp",
    local: "service-0.ns-0.svc.cluster.local:6363",
    remote: "subset-service.physics-namespace.svc.cluster.local:6363",
}' | ndndpdk-ctrl create-face | tee /dev/stderr | jq -r .id)

echo "Inserting FIB entry for /k8s/retrive-service/physics to next ndn-dpdk forwarder...."
ndndpdk-ctrl insert-fib --name /k8s/retrieve-service/physics --nexthop $NODE1FACEID_RETRIEVE

echo "Inserting FIB entry for /k8s/subset-service/physics to next ndn-dpdk forwarder...."
ndndpdk-ctrl insert-fib --name /k8s/subset-service/physics --nexthop $NODE1FACEID_SUBSET

echo "Done."
