#!/usr/bin/env python3

# Input:
# Output:
# Error:


import sys
import os
import argparse
import re
import csv
from shutil import move
from glob import glob
from hurry.filesize import size

from organizeDirs import organizeDirs
from guymagerLogMD import guymagerLogMD
from filesystemID import filesystemID
from level1Data import level1Data
from mergeOutputs import mergeOutputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with E01/info files')
    args = parser.parse_args()

    if not os.path.exists(args.inputdir):
        sys.exit('Quitting: Input directory does not exist.')

    # Check for space; quit if not available
    input_size = 0
    for dirpath, dirnames, filenames in os.walk(args.inputdir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            input_size += os.path.getsize(fp)
    print("The size of the input directory is: {0}".format(size(input_size)))
    print("To continue, you need {0} of free space.".format(size(input_size*4)))
    proceed = str(input("Do you want to continue? y/N "))
    if not proceed.startswith('y'):
        sys.exit("Quitting.")

    # Run all the individual triage scripts
    organizeDirs(args.inputdir)
    guymagerLogMD(args.inputdir)
    filesystemID(args.inputdir)
    level1Data(args.inputdir)
    mergeOutputs(args.inputdir)

if __name__ == "__main__":
    main()
