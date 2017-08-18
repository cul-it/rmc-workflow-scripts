#!/usr/bin/env python3

import csv
import os
import sys
import re
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
    toflag = ['<', '>', ':', '"', "'", '/', '\\', '|', '?', '*', '!']

    if not os.path.exists(inputdir):
        sys.exit('Quitting: Input directory does not exist')

    # Does output file exist?
    if os.path.isfile(os.path.normpath(outfile)):
        sys.exit('Output file already exists; will not overwrite.')

    # Write a test something to the file
    outwrite = open(outfile, 'w')
    outwrite.write('\t'.join(['File Path', 'Character or Issue', 'In Directory Name']))
    outwrite.write('\n')

    # Report all files under input
    allfiles = os.walk(inputdir)
    for root, subdirs, files in os.walk(inputdir):
        for f in files:
            thisfile = os.path.normpath(os.path.join(root, f)) # Full path of file
            fullpath = splitPath(thisfile)
            for fp in fullpath:
                for f in fp:
                    if f in toflag:
                        outwrite.write('\t'.join([thisfile, f,]))
                        outwrite.write('\n')
                if re.search(r'^\s|\s$', fp):
                    outwrite.write('\t'.join([thisfile, 'Leading or trailing space',]))
                    outwrite.write('\n')

    # Close output
    outwrite.close()


def splitPath(path):
    components = []
    splitTuple = os.path.split(path)
    while splitTuple != ('/', ''):
        components.append(splitTuple[1])
        splitTuple = os.path.split(splitTuple[0])
    return components


if __name__ == "__main__":
    main()
