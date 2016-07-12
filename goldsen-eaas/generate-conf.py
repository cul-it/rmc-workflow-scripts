#!/usr/bin/env python3

import glob
import os
import sys
import xml.etree.ElementTree as ET

namespaces = {'DFXML' : 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML'}

conf = {}

# NOTE TEMPORARY
inputdir = '/Users/dianne/Desktop/GoldsenMD'
inputoffset = 4

# May need to adjust in production
goldsen_files = glob.glob(os.path.join(inputdir, 'RMM', 'RMM*', 'PAFDAO', 'WORKS', '*'))

for gf in goldsen_files:
    fullpath = gf.split(os.sep)
    rmm_num = fullpath[inputoffset+1]
    conf[rmm_num] = {}

    bibid = os.path.basename(gf)
    conf[rmm_num][bibid] = {}

    # TODO: START HERE ...
    mx = glob.glob(os.path.join(gf, '*_marcxml.xml'))
    if len(mx) != 1:
        print(gf,mx)
        sys.exit('Unexpected number of marcxml files. Quitting.')
    marcxml = ET.parse(mx[0]).getroot()
    print(marcxml.getchildren())


    for di in glob.glob(os.path.join(gf, 'disk_images', '*_dfxml.xml')):
        pre_disk_image = os.path.basename(di).split('_')
        dfxml = ET.parse(di).getroot()
        vols = dfxml.findall('DFXML:volume', namespaces)
        for v in vols:
            filesystems = v.findall('DFXML:ftype_str', namespaces)
            for fs in filesystems:
                pass
#                print(fs.text)

