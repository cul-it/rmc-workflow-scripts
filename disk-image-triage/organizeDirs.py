#!/usr/bin/env python3

# Input: Directory with E01/info file pairs
# Output: Directory with one folder per each E01/info pair
#         CSV File with total file size of Exx files
# Error: Unpaired files; non-empty output directory -- script will exit

# TODO: Modularize so it can be imported in another script?

import sys
import os
import argparse
import re
import csv
from shutil import move
from glob import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with E01/info files')
#    parser.add_argument('outputdir', metavar='[output_dir]',
#                        help='output directory (initially empty) for organized files')
    args = parser.parse_args()

    try:
        os.path.exists(args.inputdir)
    except:
        sys.exit('Quitting: Input directory does not exist.')

    outputdir = os.path.join(args.inputdir, 'organized')

    try:
        dirtest = os.listdir(outputdir)
    except:
        os.makedirs(outputdir)
    else:
        if dirtest:
            sys.exit('Quitting: Output directory is not empty.')

    # Does output file exist?
    outputfile = os.path.join(args.inputdir, 'organized', 'disk_img_size.csv')

    if os.path.isfile(outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Set up output file
    outfile = open(outputfile, 'w')
    fieldnames = ['rmc_item_number', 'exx_total_size']
    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldnames)
    outfilecsv.writeheader()

    diskimgs = glob(os.path.join(args.inputdir, '*E01'))

    for di in diskimgs:
        if not os.path.isfile(di.replace('E01', 'info')):
            sys.exit('Quitting: info file not found for {0}'.format(di))
            # Nothing should be created in output if we're missing E01/info pair
            # NOTE: Does it matter if there is an info file without an E01?
    del(di)

    for di in diskimgs:
        filebase = os.path.splitext(os.path.basename(di))[0]
        pre_newdir = (re.sub('(ZD|HD|DVD|CD|FD)(\d+)', r'\g<1>'+'-'+r'\g<2>', filebase))
        newdir = os.path.join(outputdir, pre_newdir)
        os.makedirs(newdir)

        # Get every E{01..n} file
        all_di = glob(os.path.join(args.inputdir,'{0}.E*'.format(filebase)))
        total_size = 0
        for adi in all_di:
            total_size = os.path.getsize(adi)+total_size
            diskfile = os.path.join(newdir, os.path.basename(adi))
            try:
                move(adi, diskfile)
            except:
                sys.stderr.write('File not moved: {0}\n'.format(adi))

        oldinfofile = os.path.join(args.inputdir, '{0}.info'.format(filebase))
        newinfofile = os.path.join(newdir, '{0}.info'.format(filebase))
        try:
            move(oldinfofile, newinfofile)
        except:
            sys.stderr.write('File not moved: {0}\n'.format(oldinfofile))

        # Set up CSV line
        diskimg_stat = {}
        diskimg_stat['rmc_item_number'] = pre_newdir
        diskimg_stat['exx_total_size'] = total_size
        outfilecsv.writerow(diskimg_stat)

    outfile.close()

if __name__ == "__main__":
    main()
