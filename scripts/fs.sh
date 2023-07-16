#!/bin/bash

echo "Activating file server...."
jq -n '{
  face: {
    scheme: "memif",
    socketName: "/run/ndn/fileserver.sock",
    id: 0,
    role: "client",
  },
  fileServer: {
    mounts: [{
      prefix: "/k8s/retrieve-service/physics",
      path: "/srv/fs"
    },{
      prefix: "/k8s/subset-service/physics",
      path: "/srv/fs"
    }],
    segmentLen: 1100,
    uringCapacity: 4096
  }
}' | ndndpdk-ctrl --gqlserver http://127.0.0.1:3031/ activate-fileserver

echo "Done."