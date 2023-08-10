> **_NOTE:_**  This project is a work in progress. The README.md shall be constantly updated to be as comprehensive as possible.

# Description
This project contains a set of scripts to run a Kubernetes cluster with NDN applications. The cluster runs NFD
pod to listen for NDN interests and in turn perform data fetching or computation jobs. The purpose of K8s on the
project is to build a scalable NDN testbed that can be used for purpose of location indepedent content distribution, and
computing.

# Methodology
We'll setup an initial kubernetes cluster with just a single node. This node
is the gateway to the cluster and will be the only node that we can access.

This gateway node will run a single NFD which listens for incoming interests.

The incoming interest can have one of two prefixes:

1. /ndn/k8s/data: This is an interest for data fetching from the data lake. Upon receiving the 
interest, the gateway NFD will route the request to another NFD in the cluster that is attached
to the data lake.

2. /ndn/k8s/compute: This is an interest for compute request. The interest will first be parsed on the gateway node
to understand the computing requirements. The gateway node will then run a kubernetes job with the specified
requirements. The client can then poll the gateway node for the result of the computation.

# Sequence Diagram
![Sequence Diagram](sequence.png)
