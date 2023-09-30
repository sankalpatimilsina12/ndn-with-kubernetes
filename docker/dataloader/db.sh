: '
This script is responsible for loading human genome reference 
and building reference database for BLAST.
'

#!/bin/bash

# Change to the mounted PVC directory
cd /fileserver_data

if [ ! -f "GRCh38_latest_genomic.fna" ]; then
    curl -O "https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz"
    gzip -d GRCh38_latest_genomic.fna.gz
    makeblastdb -in GRCh38_latest_genomic.fna -dbtype nucl -parse_seqids -out GRCh38
else
    echo "GRCh38_latest_genomic.fna already present. Skipping download..."
fi
echo "Human genome reference loaded and BLAST database built..."
