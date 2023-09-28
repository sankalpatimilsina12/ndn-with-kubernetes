: '
This script downloads provided SRA IDs from NCBI.
'

#!/bin/bash

# Usage: ./samples.sh <file1> <file2> ...

for file in "$@"; do
    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "File $file does not exist. Skipping..."
        continue
    fi

    echo "Loading data for $file"
    mapfile -t SRA_IDS <"$file"

    for SRA_ID in "${SRA_IDS[@]}"; do
        echo "SRA ID: $SRA_ID"

        # Use esearch to get the XML record for the SRA ID
        xml_record=$(esearch -db sra -query "$SRA_ID" | efetch -format xml)

        # Get metadata
        library_strategy=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY)" - | tr " " "_")
        platform=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/EXPERIMENT/PLATFORM/ILLUMINA/INSTRUMENT_MODEL)" - | tr " " "_")
        lib_src=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SOURCE)" - | tr " " "_")
        lib_selection=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SELECTION)" - | tr " " "_")
        sample=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME)" - | tr " " "_")
        experiment=$(echo "$xml_record" | xmllint --xpath "string(//EXPERIMENT_PACKAGE/EXPERIMENT/IDENTIFIERS/PRIMARY_ID)" - | tr " " "_")

        # Construct destination directory and file names from meta data
        dest_dir="/fileserver_data/$library_strategy/$platform/$lib_src/$lib_selection/$sample/$experiment"

        # Check if destination file already exists
        dest_file="$dest_dir/$SRA_ID.sralite"
        if [ -f "$dest_file" ]; then
            echo "Destination file $dest_file already exists. Skipping..."
            continue
        fi

        echo "Downloading $SRA_ID to $dest_dir..."
        mkdir -p $dest_dir
        # Check for already downloaded file
        if ls "$dest_dir/$SRA_ID.sra"* 1> /dev/null 2>&1; then
            echo "$SRA_ID already downloaded. Skipping download..."
            continue
        fi
        prefetch -O $dest_dir $SRA_ID
        # Check if prefetch was successful
        if [ $? -ne 0 ]; then
            echo "Prefetch for $SRA_ID failed. Skipping further steps..."
            continue
        fi
        # Check if any .sra or .sralite file was actually downloaded
        if [ -z "$(ls $dest_dir/$SRA_ID/*.sra* 2>/dev/null)" ]; then
            echo "No .sra files found for $SRA_ID after prefetch. Skipping further steps..."
            continue
        fi
        # Move the sra and sralite files from the SRA_ID directory to the dest_dir
        mv $dest_dir/$SRA_ID/*.sra* $dest_dir
        # Remove the now empty SRA_ID directory
        rm -rf $dest_dir/$SRA_ID

        # Run fastq-dump on the SRA file for BLAST
        echo "Running fastq-dump on $SRA_ID for BLAST..."
        fastq-dump $dest_dir/$SRA_ID.sra* -O /fileserver_data/
    done
done

echo "Sample loading complete..."
