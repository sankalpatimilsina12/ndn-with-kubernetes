: '
This script is responsible for following tasks:
1. Loading sample SRAs from NCBI
2. Loading human genome reference and building reference database for BLAST 
'

#!/bin/bash

echo "Loading sample SRAs from NCBI..."
source ./samples.sh "$@"

echo "Loading human genome reference and building reference database for BLAST..."
source ./db.sh

echo "Loaded sample SRAs from NCBI and human genome reference..."
