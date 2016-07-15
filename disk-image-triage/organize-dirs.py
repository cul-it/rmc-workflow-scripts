#!/usr/bin/env python3

# Input: Directory with E01/info file pairs
# Output: Directory with one folder per each E01/info pair
# Error: Unpaired files; non-empty output directory -- script will exit

# TODO: Modularize so it can be imported in another script?

import sys
import os
import argparse
import re
from shutil import copyfile
from glob import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with E01/info files')
    parser.add_argument('outputdir', metavar='[output_dir]',
                        help='output directory (initially empty) for organized files')
    args = parser.parse_args()

    try:
        os.path.exists(args.inputdir)
    except:
        sys.exit('Quitting: Input directory does not exist.')

    try:
        dirtest = os.listdir(args.outputdir)
    except:
        sys.exit('Quitting: Output directory does not exist.')
    else:
        if dirtest:
            sys.exit('Quitting: Output directory is not empty.')

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
        newdir = os.path.join(args.outputdir, pre_newdir)
        os.makedirs(newdir)

        # Get every E{01..n} file
        all_di = glob(os.path.join(args.inputdir,'{0}.E*'.format(filebase)))
        for adi in all_di:
            diskfile = os.path.join(newdir, os.path.basename(adi))
            copyfile(adi, diskfile) # Copy only

        oldinfofile = os.path.join(args.inputdir, '{0}.info'.format(filebase))
        newinfofile = os.path.join(newdir, '{0}.info'.format(filebase))
        copyfile(oldinfofile, newinfofile) # Copy only

if __name__ == "__main__":
    main()
