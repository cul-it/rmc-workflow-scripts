#!/usr/bin/env python3

import re
import os
import subprocess
import sys
import glob
import argparse

# Input: Directory of directories of E01/info pairs (or triples, etc.)
# Output: CSV file with ID, list of filesystems
#         Raw disk image if a.) multiple filesystems exist
#                           b.) single filesystem unsupported by TSK
#         Filesystems in json? in output directory? for easy parsing later?
# Error: Input directory in wrong format
#        EnCase disk image fails to extract
#        ...?!

fs_search = re.compile('(.*) file system')

# TEMPORARY INPUT FOR TESTING
pre_disktype_res = open('alldisktype.txt', 'rU').read().split('---')
disktype_res_tmp = []
for dr in pre_disktype_res[1:]:
    dr = dr.strip()
    disktype_res_tmp.append(dr)

def parse_disktype(disktype_res):
    filesystems = []
    disktype_res = disktype_res.split('\n')
    for dr in disktype_res:
        fs_try = fs_search.search(dr)
        if fs_try is not None:
            filesystems.append(fs_try.group(1).strip())
    return filesystems

def extract_raw(disk_img_dir):
    # NEEDED: verified directory
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with directories of E01/info pairs')
    parser.add_argument('outputfile', metavar='[output_file]',
                        help='output file for CSV data')
    args = parser.parse_args()

    # Does output dir exist?
    try:
        os.path.exists(args.inputdir)
    except:
        sys.exit('Quitting: Input directory does not exist.')

    # Does output file exist?
    if os.path.isfile(args.outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Set up output file
    # TODO DO THIS

    # Get list of dirs
    dirlist = glob.glob('{0}/*'.format(args.inputdir,))

# TEST EWFEXPORT WITH E01/E02 files
    for dl in dirlist:
        ewf_files = glob.glob('{0}/*.E*'.format(dl))
        basename = os.path.basename(os.path.splitext(ewf_files[0])[0])
        command = 'ewfexport -u -t {0} {1}'.format(basename, ' '.join(ewf_files))
        print(command)
        


#    # TEMPORARY TESTING LOOP
#    for disktype_res_item in disktype_res_tmp:
#        print(parse_disktype(disktype_res_item))
#        print("end of this!\n\n")
#
#    # TODO: Write out CSV with key (from directory)
#    # TODO: unpack the EnCase disk image

if __name__ == "__main__":
    main()
