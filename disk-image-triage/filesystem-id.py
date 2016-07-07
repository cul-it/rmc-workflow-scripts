#!/usr/bin/env python3

import re
import subprocess

# TODO: unpack the EnCase disk image

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

# TEMPORARY TESTING LOOP
for disktype_res_item in disktype_res_tmp:
    print(parse_disktype(disktype_res_item))
    print("end of this!\n\n")

# TODO: Write out CSV with key (from directory)
