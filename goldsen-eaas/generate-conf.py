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


def scrub_marc(marc):
    marc = marc.rstrip(',')
    marc = marc.rstrip(' :')
    marc = marc.rstrip(' /')
    marc = marc.rstrip('.')
    marc = marc.rstrip(',')
    return marc


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
        title = None
        creator = None
        alt_creator = None
        date = None

        for df in datafields:
            if df.get('tag') == '538':
                df_children = df.getchildren()
                for dfc in df_children:
                    sysreqs.append(dfc.text)
            elif df.get('tag') == '245':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'a':
                        title = scrub_marc(dfc.text)
                    elif dfc.get('code') == 'c':
                        creator = scrub_marc(dfc.text)
            elif df.get('tag') == '100':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'a':
                        alt_creator = scrub_marc(dfc.text)
            elif df.get('tag') == '260':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'c':
                        date = scrub_marc(dfc.text)
                        date = date.lstrip('c')
                        date = date.strip('?')
                        date = date.strip('[')
                        date = date.strip(']')

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
            conf[disk_image_id]['title'] = title
            conf[disk_image_id]['date'] = date

            if (creator is None) and (alt_creator is None):
                conf[disk_image_id]['creator'] = ''
            elif (alt_creator is not None) and (creator is None):
                conf[disk_image_id]['creator'] = alt_creator
            elif (creator is not None):
                conf[disk_image_id]['creator'] = creator

            # This will work when we have the whole CULAR shebang
            conf[disk_image_id]['disk_img'] = glob.glob(os.path.join(gf, 'disk_images', '*.dd'))

    return conf

def conf2tmpl(conf_entry):
    # create empty directory for destination of templates
    # First go through conf file and figure out what's needed to be created
    for entry in conf_entry.keys():
        print(entry)
#    pass

def main():
    goldsenconf = parse_md()
    conf2tmpl(goldsenconf)

if __name__ == "__main__":
    main()
