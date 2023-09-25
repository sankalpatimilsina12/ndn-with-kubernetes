: '
This script is responsible for loading human genome reference 
and building reference database for BLAST.
'

#!/bin/bash

# Usage: ./db.sh

# Change to the mounted PVC directory
cd /fileserver_data

curl -O "https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz"
gzip -d GRCh38_latest_genomic.fna.gz
makeblastdb -in GRCh38_latest_genomic.fna -dbtype nucl -parse_seqids -out GRCh38
echo "Human genome reference loaded and BLAST database built..."
