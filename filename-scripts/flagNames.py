#!/usr/bin/env python3

import csv
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory that contains filenames to scan')
    parser.add_argument('outfile', metavar='[output_file]',
                        help='output file for results')
    args = parser.parse_args()
    idir = args.inputdir
    iout = args.outfile

    flagNames(idir, iout)

def flagNames(inputdir, outfile):
    if not os.path.exists(inputdir):
        sys.exit('Quitting: Input directory does not exist')

    # Does output file exist?
    if os.path.isfile(os.path.normpath(outfile)):
        sys.exit('Output file already exists; will not overwrite.')

    # Write a test something to the file
    outwrite = open(outfile, 'w')

    # Report all files recursively under input
    allfiles = os.walk(inputdir)
    outwrite.write('test it out!!!')

    # Close output
    outwrite.close()


if __name__ == "__main__":
    main()
