: '
This script is responsible for loading NCBI data into PVC. 
It uses the SRA toolkit"s prefetch command to download the data.
'

#!/bin/bash

# Usage: ./dataloader.sh <file1> <file2> ...

for file in "$@"; do
    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "File $file does not exist. Skipping..."
        continue
    fi

    # Derive destination directory name from filename by removing .txt extension
    dest_dir="/fileserver_data/$(basename "$file" .txt)"

    # Check if destination directory already exists
    if [ -d "$dest_dir" ]; then
        echo "Destination directory $dest_dir already exists. Skipping..."
        continue
    fi

    echo "Loading data for $file"
    while IFS= read -r SRA_ID; do
        echo "Downloading $SRA_ID..."
        mkdir -p $dest_dir
        prefetch -O $dest_dir $SRA_ID
    done <"$file"
done
