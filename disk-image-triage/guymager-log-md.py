#!/usr/bin/env python3

# Originally from revision of GuymagerLogParser
# https://github.com/euanc/GuymagerLogParser/commit/2aab1e4ddf87a5b759e834414e7b3e4e99addcfa
# Column headings changed to reflect RMC process

# Input: Directory of directories of E01/info pairs (or triples, etc.)
# Output: CSV File with aggregated metadata from .info files
# Error: output file already exists -- script will exit

import os
import sys
import re
import argparse
import csv
from glob import glob

# set input variables for the source and destination file directories
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with directory of E01/info pairs')
#    parser.add_argument('outputfile', metavar='[output_file]',
#                        help='output file for CSV data')
    args = parser.parse_args()

    try:
        os.path.exists(args.inputdir)
    except:
        sys.exit('Quitting: Input directory does not exist.')

    # Does output file exist?
    outputfile = os.path.join(args.inputdir, 'image_info.csv')

    if os.path.isfile(outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Set up output file
    outfile = open(outputfile, 'w')
    fieldnames = ['rmc_accession','rmc_item_number', 'technician', 'file_path','disk_image_format',
                  'ewf_disk_image_size','acquire_date', 'acquisition_time', 'raw_md5_hash',
                  'number_sector_errors']
    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldnames)
    outfilecsv.writeheader()

    files = glob(os.path.join(args.inputdir, '*/*.info'))

    for filename in files:
        parsedline = {}
        for line in open(filename, 'rU'): 

            if line.strip().startswith('Case number'):
                parsedline['rmc_accession'] = line[26:].strip()

            if line.strip().startswith('Evidence number'):
                parsedline['rmc_item_number'] = line[26:].strip()

            if line.strip().startswith('Examiner'):
                parsedline['technician'] = line[26:].strip()
                
            if line.strip().startswith('Image path and file name'):
                parsedline['file_path'] = line[26:].strip()
            
            if line.strip().startswith('Device size'):
                parsedline['ewf_disk_image_size'] = line[26:].split()[0]
                
            if line.strip().startswith('Ended'):
                parsedline['acquire_date'] = line[22:41]
                elapsed = re.match('(\d+) hours, (\d+) minutes and (\d+) seconds', line[43:].strip())
                elapsedtotal = (3600*int(elapsed.group(1))) + (60*int(elapsed.group(2))) + int(elapsed.group(3))
                parsedline['acquisition_time'] = elapsedtotal
                
            if line.strip().startswith('MD5 hash verified image'):
                parsedline['raw_md5_hash'] = line[28:].strip()
                
            if line.strip().startswith('Format'):
                parsedline['disk_image_format'] = line[26:].strip()

            if line.strip().startswith('State'):
                badsectors = re.search('with (\d+) bad sectors', line)
                if badsectors:
                    badsectorcount = badsectors.group(1)
                else:
                    badsectorcount = '0'
                parsedline['number_sector_errors'] = badsectorcount

        outfilecsv.writerow(parsedline)

    outfile.close()

if __name__ == "__main__":
    main()
