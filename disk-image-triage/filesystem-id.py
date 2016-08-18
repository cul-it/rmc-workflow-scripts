#!/usr/bin/env python3

import re
import os
import subprocess
import sys
import argparse
import csv
from glob import glob

# Input: Directory of directories of E01/info pairs (or triples, etc.)
# Output: CSV file with ID, list of filesystems
#         Raw disk image if a.) multiple filesystems exist
#                           b.) single filesystem unsupported by TSK
#         Filesystems in json? in output directory? for easy parsing later?
# Error: Input directory in wrong format <-- NOTE: do I actually test for this?
#        EnCase disk image fails to extract
#        Incorrect number of raw files found in directory (!= 1)
#        Disktype fails on input

fs_search = re.compile('(.*) file system')


def parse_disktype(disktype_res):
    filesystems = []
    disktype_res = disktype_res.split('\n')
    for dr in disktype_res:
        fs_try = fs_search.search(dr)
        if fs_try is not None:
            filesystems.append(fs_try.group(1).strip())
    return filesystems

def run_disktype(pathtoraw):
    disktype_output = []
    for rdir in pathtoraw:
        rawfiles = glob(os.path.join(rdir, '*.raw'))
        if len(rawfiles) != 1:
            sys.exit("Unexpected number of raw files found.")
        dtcommand = ['disktype', rawfiles[0]]
        try:
            dtout = subprocess.check_output(dtcommand)
        except:
            sys.exit("disktype failed with {0}".format(rawfiles[0]))
        dtout = dtout.decode('utf-8')

        fsondisk = parse_disktype(dtout)
        disktype_output.append({'rmc_item_number' : os.path.basename(rdir), 'file_system_type' : '|'.join(fsondisk)})
#        disktype_output[os.path.basename(rdir)] = fsondisk
    return disktype_output

def extract_raw(dirlist, startdir):
    for dl in dirlist:
        os.chdir(startdir)
        ewf_files = glob(os.path.join(dl, '*.E*'))
        ewf_files.sort()
        ewf_files = [os.path.basename(eb) for eb in ewf_files]
        basename = os.path.basename(os.path.splitext(ewf_files[0])[0])

        os.chdir(dl)
        command = 'ewfexport -u -t {0} {1}'.format(basename, ' '.join(ewf_files))
        command = command.split(' ')
        try:
            subprocess.call(command)
        except:
            sys.exit("ewfexport error in {0}.".format(dl))




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory with directories of E01/info pairs')
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
    fieldnames = ['rmc_item_number', 'file_system_type'] 
    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldnames)
    outfilecsv.writeheader()

    # Start making things happen
    scriptloc = os.getcwd()

    # Get list of dirs and run ewfexport for Exx files in each
    disk_img_dir = glob(os.path.join(args.inputdir,'*',))
    extract_raw(disk_img_dir, scriptloc)

    # Return to start point
    os.chdir(scriptloc)

    # Run disktype on all *.raw files
    fsdict = run_disktype(disk_img_dir)

    # Load into output CSV
    for line in fsdict:
        outfilecsv.writerow(line)





if __name__ == "__main__":
    main()
