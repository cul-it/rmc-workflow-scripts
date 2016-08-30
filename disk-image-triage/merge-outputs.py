#!/usr/bin/env python3

import csv
import os
import sys
import argparse

# Input: Directory of directories of E01/info pairs (or triples, etc.)
# Output: Aggregated CSV file that combines outputs of previous steps
#         This includes:
#           1. image_info.csv
#           2. filesystem.csv
#           3. level1.csv
# Error: Input directory does not exist, or
#        Output file already exists, or
#        Any of the input csv files do not exist; script will exit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory that contains "organized" subdirectory')
    args = parser.parse_args()

    # Does input dir exist?
    if not os.path.exists(os.path.join(args.inputdir, 'organized')):
        sys.exit('Quitting: Input directory does not exist.')


    # Does output file exist?
    inputbase = os.path.abspath(os.path.normpath(args.inputdir)).split(os.sep)[-1]
    outputfile = os.path.join(args.inputdir, '{0}_stabilization.csv'.format(inputbase))

    if os.path.isfile(outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Ideally writing like this means if there are more intermediate steps
    # it is trivial to aggregate their data. One can only hope.
    input_csvs = ['image_info.csv', 'filesystem.csv', 'level1.csv', 'disk_img_size.csv']
    aggregating_col = 'rmc_item_number'

    stabilization_dict = {}
    fieldlist = []

    for ic in input_csvs:
        with open(os.path.join(args.inputdir, 'organized', ic)) as csvfile:
            reader = csv.DictReader(csvfile)
            for rk in reader.fieldnames:
                if rk not in fieldlist:
                    fieldlist.append(rk)
            for row in reader:
                # Add values to stabilization_dict
                try:
                    stabilization_dict[row['rmc_item_number']].update(row)
                except KeyError:
                    stabilization_dict[row['rmc_item_number']] = row


    outfile = open(outputfile, 'w')

    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldlist)
    outfilecsv.writeheader()

    for rin in stabilization_dict.keys():
        outfilecsv.writerow(stabilization_dict[rin])


if __name__ == "__main__":
    main()
