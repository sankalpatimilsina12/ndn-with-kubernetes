# Description
This project contains a set of scripts to run a Kubernetes cluster with NDN networking. The cluster runs NFD
pod to listen for NDN interests and in turn perform data fetching or computation jobs. The purpose of K8s on the
project is to build a scalable NDN network that can be used for purpose of location indepedent content distribution, and
computing.

Please refer to [process.txt](process.txt) for the technical details of the project.

# Sequence Diagram
![Sequence Diagram](sequence.png)