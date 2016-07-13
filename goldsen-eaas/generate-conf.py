#!/usr/bin/env python3

import glob
import os
import sys
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

namespaces = {'dfxml' : 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML',
              'marc' : 'http://www.loc.gov/MARC21/slim'}


# NOTE TEMPORARY
inputdir = '/Users/dianne/Desktop/GoldsenMD'
inputoffset = 5


def parse_md():
    conf = defaultdict(dict)

    # Adjust in production
    goldsen_files = glob.glob(os.path.join(inputdir, 'RMM', 'RMM*', 'PAFDAO', 'WORKS', '*'))

    for gf in goldsen_files:
        fullpath = gf.split(os.sep)
        rmm_num = fullpath[inputoffset+1]
        bibid = os.path.basename(gf)

        mx = glob.glob(os.path.join(gf, '*_marcxml.xml'))
        if len(mx) != 1:
            print(gf,"Missing MARCXML") # TEMPORARY WORKAROUND
            continue # TEMPORARY WORKAROUND
    #        sys.exit('Unexpected number of marcxml files. Quitting.') 
    # This should actually happen

        marcxml = ET.parse(mx[0]).getroot()
        record = marcxml.getchildren()[0]
        datafields = record.findall('marc:datafield', namespaces)
        sysreqs = []
        for df in datafields:
            if df.get('tag') == '538':
                df_children = df.getchildren()
                for dfc in df_children:
                    sysreqs.append(dfc.text)

        for di in glob.glob(os.path.join(gf, 'disk_images', '*_dfxml.xml')):
            pre_disk_image = os.path.basename(di).split('_')
            disk_image_id = '{0}_{1}'.format(bibid, pre_disk_image[1])
            dfxml = ET.parse(di).getroot()
            vols = dfxml.findall('dfxml:volume', namespaces)
            for v in vols:
                filesystems = []
                pre_filesystems = v.findall('dfxml:ftype_str', namespaces)
                for fs in pre_filesystems:
                    filesystems.append(fs.text)

            # Set up conf
            conf[disk_image_id] = {}
            conf[disk_image_id]['RMM'] = rmm_num
            conf[disk_image_id]['sysreq'] = sysreqs
            conf[disk_image_id]['filesystems'] = filesystems
            # TODO: Actual disk image filename
            # TODO: Title from MARC Record
            

    return conf

def main():
    goldsenconf = parse_md()
    print(goldsenconf)

if __name__ == "__main__":
    main()
