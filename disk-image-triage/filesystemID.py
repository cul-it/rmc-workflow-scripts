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

def run_disktype(rdir):
    disktype_output = {}
    disktype_output['rmc_item_number'] = os.path.basename(rdir)

    rawfiles = glob(os.path.join(rdir, '*.raw'))

    if len(rawfiles) != 1:
        sys.stderr.write("Wrong number of RAW files: {0}\n".format(rdir))
        disktype_output['file_system_type'] = 'ERROR'
        return disktype_output

    dtcommand = ['disktype', rawfiles[0]]
    try:
        dtout = subprocess.check_output(dtcommand)
    except:
        sys.stderr.write("disktype failed: {0}\n".format(rawfiles[0]))
        disktype_output['file_system_type'] = 'ERROR'
        return disktype_output


    # Fallback for some weird encoding issues
    # Nested try/except isn't terribly pretty but oh well
    try:
        dtout = dtout.decode('utf-8')
    except:
        try:
            dtout = dtout.decode('iso-8859-1')
        except:
            dtout = None 

    if dtout is None:
        fsondisk = ['ERROR']
    else:
        fsondisk = parse_disktype(dtout)

    disktype_output['file_system_type']  = '|'.join(fsondisk)
    return disktype_output

def extract_raw(dl, startdir):
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
        sys.stderr.write("EWF extraction failed: {0}.\n".format(dl))
        dtout = ['ERROR']
        return dtout

    dtout = run_disktype(dl) # OH MAN I HOPE THIS ACTUALLY WORKS
    return dtout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', metavar='[input_dir]',
                        help='input directory that contains "organized" subdirectory')
#    parser.add_argument('outputfile', metavar='[output_file]',
#                        help='output file for CSV data')
    args = parser.parse_args()

    # Does input dir exist?
    if not os.path.exists(os.path.join(args.inputdir, 'organized')):
        sys.exit('Quitting: Input directory does not exist.')

    # Does output file exist?
    outputfile = os.path.join(args.inputdir, 'organized' ,'filesystem.csv')

    if os.path.isfile(outputfile):
        sys.exit('Output file already exists; will not overwrite.')

    # Set up output file
    outfile = open(outputfile, 'w')
    fieldnames = ['rmc_item_number', 'file_system_type'] 
    outfilecsv = csv.DictWriter(outfile, fieldnames=fieldnames)
    outfilecsv.writeheader()

    # Start making things happen
    scriptloc = os.getcwd()

    # Get list of dirs
    disk_img_dir = glob(os.path.join(os.path.abspath(args.inputdir), 'organized', '*',))

    # Remove any csv files here
    disk_img_dir = [did for did in disk_img_dir if not did.endswith('.csv')]

    # Run ewfexport for Exx files in dirs
    # Run disktype within raw extraction function
    # Write out as loop proceeds
    for did in disk_img_dir:
        dtres = extract_raw(did, scriptloc)
        outfilecsv.writerow(dtres)


if __name__ == "__main__":
    main()
