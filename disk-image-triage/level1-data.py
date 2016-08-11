#!/usr/bin/env python3

#!/usr/bin/env python3

import subprocess
import argparse
import os
import sys
import csv
from glob import glob

# Input: Directory of directories of E01/info pairs (or triples, etc.)
# Output: CSV file with aggregated metadata
#         bulk_extractor output in appropriate directory, when produced.
# Error: Input directory in wrong format <-- NOTE: Do I check for that?

# NOTE: bulk_extractor is agnostic about filesystem:
# See http://www.forensicswiki.org/wiki/Bulk_extractor 


def detect_beout(bedir):
    # Reports back which files are non-zero
    accts = {'alerts.txt': 0,
             'ccn_track2.txt': 0,
             'ccn.txt': 0,
             'pii.txt': 0,
             'telephone.txt': 0
            }
    for ats in accts.keys():
        if os.stat(os.path.join(bedir, ats)).st_size > 0:
            accts[ats] = 1

    return accts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with directories of E01/info'+                             ' pairs and RAW extracted disk images')
    parser.add_argument('outputfile', metavar='[output_file]',
                        help='output file for CSV data')
    args = parser.parse_args()

    # Does input dir exist?
    try:
        os.path.exists(args.inputdir)
    except:
        sys.exit('Quitting: Input directory does not exist.')

    # Does output file exist?
    if os.path.isfile(args.outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Set up output file
    outfile = open(args.outputfile, 'w')
    fieldnames = ['rmc_item_number', 'alerts.txt', 'ccn_track2.txt',
                  'ccn.txt', 'pii.txt', 'telephone.txt']
    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldnames)
    outfilecsv.writeheader()


    # Get list of dirs first
    disk_img_dir = glob(os.path.join(args.inputdir, '*',))

    # Set up output file
    outfile = ''

    # Starting dir
    startdir = os.getcwd()

    # Loop through and check for RAW files
    for did in disk_img_dir:
        rawfiles = glob(os.path.join(did, "*.raw"))
        if len(rawfiles) != 1:
            sys.exit('Unexpected number of RAW files in {0}'.format(did))
        else:
            this_raw = os.path.basename(rawfiles[0])

        # Generate outputdir name
        beout = '{0}_BE'.format(os.path.basename(did))

        # Go to dir
        os.chdir(did)

        # Set up bulk_extractor command with ONLY the accts scanner enabled
        becommand = ['bulk_extractor', this_raw, 
                     '-E', 'accts', '-o', beout]

        # Run the command
        spbeout = subprocess.check_output(becommand)

        # Get bulk_extractor results
        beres = detect_beout(beout)

        # Add RMC identifier and write to log
        beres['rmc_item_number'] = os.path.basename(did)
        outfilecsv.writerow(beres)

        # Return to start directory
        os.chdir(startdir)


if __name__ == "__main__":
    main()
