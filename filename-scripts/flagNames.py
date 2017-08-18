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
    toflag = ['<', '>', ':', '"', "'", '/', '\\', '|', '?', '*', '!']
    # TODO: Leading or trailing spaces


    if not os.path.exists(inputdir):
        sys.exit('Quitting: Input directory does not exist')

    # Does output file exist?
    if os.path.isfile(os.path.normpath(outfile)):
        sys.exit('Output file already exists; will not overwrite.')

    # Write a test something to the file
#    outwrite = open(outfile, 'w')
    print('\t'.join(['File Path', 'Character or Issue', 'In Directory Name']))

    # Report all files under input
    allfiles = os.walk(inputdir)
    for root, subdirs, files in os.walk(inputdir):
        for f in files:
            thisfile = os.path.normpath(os.path.join(root, f)) # Full path of file
            fullpath = splitPath(thisfile)
            indir = False
            for i,fp in enumerate(fullpath):
                if i > 1:
                    indir = True
                for f in fp:
                    if f in toflag:
                        print('\t'.join([thisfile, f, str(indir)]))


def splitPath(path):
    components = []
    splitTuple = os.path.split(path)
    while splitTuple != ('/', ''):
        components.append(splitTuple[1])
        splitTuple = os.path.split(splitTuple[0])
    return components



    # Close output
#    outwrite.close()


if __name__ == "__main__":
    main()
